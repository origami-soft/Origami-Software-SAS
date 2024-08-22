# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AbstractAccountPaymentImputationLine(models.AbstractModel):
    _name = 'abstract.payment.imputation.line'
    _description = 'Linea de imputación abstracto'

    @api.depends(
        'payment_id.payment_date', 'company_currency_id', 'move_line_id.amount_residual',
        'move_line_id.balance', 'move_line_id.amount_currency', 'move_line_id.amount_residual_currency'
    )
    def _compute_amounts(self):
        """ Calculo los restantes y totales según la fecha elegida en el pago """
        for line in self:
            date = line.payment_id._get_payment_date()
            company = line.move_line_id.company_id
            move_line_currency = line.move_line_id.currency_id
            currency = line.company_currency_id
            residual = abs(line.move_line_id.amount_residual_currency) if line.move_line_id.amount_currency \
                else abs(line.move_line_id.amount_residual)
            total = abs(line.move_line_id.amount_currency) if line.move_line_id.amount_currency \
                else abs(line.move_line_id.balance)
            line.update({
                'amount_residual': residual,
                'amount_total': total,
                'amount_residual_company': move_line_currency._convert(residual, currency, company, date),
                'amount_total_company': move_line_currency._convert(total, currency, company, date),
            })

    @api.depends('payment_id.payment_date', 'company_currency_id', 'payment_currency_id')
    def _get_payment_amounts(self):
        for line in self:
            company_currency = line.company_currency_id
            payment_currency = line.payment_currency_id
            date = line.payment_id._get_payment_date()
            company = line.move_line_id.company_id
            residual = company_currency._convert(
                line.amount_residual_company, payment_currency, company, date
            ) if payment_currency != line.currency_id else line.amount_residual
            total = company_currency._convert(
                line.amount_total_company, payment_currency, company, date
            ) if payment_currency != line.currency_id else line.amount_total
            line.update({
                'amount_residual_in_payment_currency': residual,
                'amount_total_in_payment_currency': total,
            })

    def _compute_currency_id(self):
        for line in self:
            line.currency_id = line.move_line_id.currency_id or line.move_line_id.company_currency_id

    def _compute_name(self):
        for line in self:
            line.name = line.move_line_id.name or line.move_line_id.move_id.name

    payment_id = fields.Many2one('account.payment')
    name = fields.Char('Nombre', compute='_compute_name')
    move_line_id = fields.Many2one('account.move.line', 'Documento')
    move_line_date = fields.Date('Fecha', related='move_line_id.date')
    move_line_date_maturity = fields.Date('Fecha de vencimiento', related='move_line_id.date_maturity')
    currency_id = fields.Many2one('res.currency', compute='_compute_currency_id')
    company_currency_id = fields.Many2one(related='move_line_id.company_currency_id')
    amount_residual = fields.Monetary('Restante moneda comprobante', compute='_compute_amounts')
    amount_total = fields.Monetary('Total moneda comprobante', compute='_compute_amounts')
    amount_residual_company = fields.Monetary('Restante moneda empresa', compute='_compute_amounts')
    amount_total_company = fields.Monetary('Total moneda empresa', compute='_compute_amounts')
    full_reconcile = fields.Boolean('Conciliacion completa')
    company_id = fields.Many2one(
        'res.company',
        string='Compania',
        related='move_line_id.company_id',
        store=True,
        readonly=True,
        related_sudo=False
    )
    concile = fields.Boolean('Imputar total')
    amount = fields.Monetary('Total A imputar', currency_field='payment_currency_id')
    payment_currency_id = fields.Many2one(related='payment_id.currency_id', readonly=True)
    amount_residual_in_payment_currency = fields.Monetary(
        compute='_get_payment_amounts',
        currency_field='payment_currency_id'
    )
    amount_total_in_payment_currency = fields.Monetary(
        compute='_get_payment_amounts',
        currency_field='payment_currency_id'
    )

    def check_imputation_amount(self):
        for r in self:
            if r.amount < 0:
                raise ValidationError("No se pueden imputar importes negativos")
            if round(r.amount_residual_in_payment_currency, 2) < round(r.amount, 2) and not r.full_reconcile:
                raise ValidationError("No se pueden imputar importes mayores que lo que reste pagar "
                                      "sin definir una conciliación completa")

    @api.onchange('full_reconcile')
    def onchange_full_reconcile_account(self):
        if self.amount == self.amount_residual_in_payment_currency:
            self.full_reconcile = False

    @api.onchange('concile')
    def onchange_concile(self):
        if self.concile:
            self.amount = self.amount_residual_in_payment_currency
            self.full_reconcile = False

    @api.onchange('amount')
    def onchange_amount(self):
        self.concile = self.amount == self.amount_residual_in_payment_currency

    def validate(self, invoice_move_line):
        """
        Valida que no haya problemas a la necesitar generar una imputacion a una invoice
        :param invoice_move_line: account.move.line de la invoice
        """
        self.ensure_one()
        # Caso que se modifique el asiento y deje inconsistencia
        if len(invoice_move_line) != 1:
            raise ValidationError("El asiento de la factura que se quiere imputar no tiene cuentas deudoras "
                                  "o tiene mas de una asociada, por favor, modificar el asiento primero")
        self.check_imputation_amount()


class PaymentImputationLine(models.Model):
    _name = 'payment.imputation.line'
    _description = 'Línea de imputación de pago'
    _inherit = 'abstract.payment.imputation.line'

    payment_id = fields.Many2one('account.payment', 'Pago', ondelete='cascade')
    payment_state = fields.Selection(related='payment_id.state')
    move_line_id = fields.Many2one(ondelete="restrict")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
