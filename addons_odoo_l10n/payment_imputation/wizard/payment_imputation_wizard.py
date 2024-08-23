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
ROUND_PRECISION = 2


class PaymentImputationWizard(models.TransientModel):
    _name = 'payment.imputation.wizard'
    _description = 'Wizard de imputacion de pagos'

    @api.depends('debit_imputation_line_ids', 'advance_amount', 'credit_imputation_line_ids')
    def _get_total_payment(self):
        self.total = round(
            sum(self.debit_imputation_line_ids.mapped('amount'))
            - sum(self.credit_imputation_line_ids.mapped('amount'))
            + self.advance_amount, ROUND_PRECISION)

    partner_id = fields.Many2one('res.partner', 'Partner', required=True)
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id
    )
    payment_type = fields.Selection([('inbound', 'Inbound'), ('outbound', 'Outbound')], 'Tipo')
    advance_amount = fields.Float('Importe a cuenta')
    journal_id = fields.Many2one(
        'account.journal',
        domain=[('type', 'in', ('bank', 'cash'))],
        required=True
    )
    debit_imputation_line_ids = fields.One2many(
        'payment.imputation.debit.line.wizard',
        'payment_id',
        'Débitos',
    )
    credit_imputation_line_ids = fields.One2many(
        'payment.imputation.credit.line.wizard',
        'payment_id',
        'Créditos',
    )
    total = fields.Float('Total', compute=_get_total_payment)
    payment_date = fields.Date('Fecha')

    amount_to_pay = fields.Float(string='Total a pagar')

    amount_left = fields.Float(string='Faltante a pagar', compute="_compute_amount_left")
    company_id = fields.Many2one(
        'res.company',
        related='journal_id.company_id'
    )

    @api.depends('amount_to_pay', 'total')
    def _compute_amount_left(self):
        self.amount_left = self.amount_to_pay - self.total

    @api.constrains('amount_to_pay')
    def _constrain_amount_to_pay(self):
        self.ensure_one()
        if self.amount_to_pay <= 0 and self.payment_type == 'inbound':
            raise ValidationError("El total a pagar tiene que ser mayor a 0")

    def _get_payment_date(self):
        self.ensure_one()
        return self.payment_date or fields.Date.today()

    @api.onchange('payment_type')
    def onchange_type(self):
        partner_type = 'customer' if self.payment_type == 'inbound' else 'supplier'
        return {'domain': {'search_mode': partner_type}}

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        currency = self.journal_id.currency_id
        self.update({
            'debit_imputation_line_ids': None,
            'credit_imputation_line_ids': None,
        })
        lines = self._get_move_lines(currency.id) if self.partner_id and self.journal_id else None
        debit_lines = [(0, 0, {
            'move_line_id': line.id
        }) for line in lines.get('debit_lines')] if lines and lines.get('debit_lines') else None
        credit_lines = [(0, 0, {
            'move_line_id': line.id
        }) for line in lines.get('credit_lines')] if lines and lines.get('credit_lines') else None
        self.update({
            'debit_imputation_line_ids': debit_lines,
            'credit_imputation_line_ids': credit_lines
        })
    
    def _get_move_lines_domain(self, account_type, currency_id):
        domain = [
            ('account_id.user_type_id.type', '=', account_type),
            ('partner_id', '=', self.partner_id.id),
            ('reconciled', '=', False),
            ('amount_residual', '!=', 0.0),
            ('currency_id', '=', currency_id),
            ('move_id.state', '=', 'posted'),
            ('company_id', '=', self.company_id.id)
        ]
        if currency_id:
            domain.append(('amount_residual_currency', '!=', 0.0))
        return domain

    def _get_move_lines(self, currency_id=None):
        account_type = 'receivable' if self.payment_type == 'inbound' else 'payable'
        search_domain = self._get_move_lines_domain(account_type, currency_id)

        lines = self.env['account.move.line'].search(search_domain)
        return {
            'debit_lines':  lines.filtered(lambda x: x.debit > 0 if account_type == 'receivable' else x.credit > 0),
            'credit_lines': lines.filtered(lambda x: x.credit > 0 if account_type == 'receivable' else x.debit > 0)
        }

    @api.onchange('journal_id')
    def onchange_journal_id(self):
        if self.journal_id:
            self.onchange_partner_id()
            self.currency_id = self.journal_id.currency_id or self.journal_id.company_id.currency_id
            for l in self.debit_imputation_line_ids:
                l._get_payment_amounts()
                l.onchange_concile()
            for l in self.credit_imputation_line_ids:
                l._get_payment_amounts()
                l.onchange_concile()

    def create_payment(self):
        self._validate_payment_imputation()
        self.reconcile_credits()
        self.debit_imputation_line_ids.check_imputation_amount()
        payment = self.env['account.payment'].create(self._get_payment_vals())

        return {
            'name': 'Pago',
            'views': [[False, "form"], [False, "tree"]],
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'res_id': payment.id,
        }

    def _get_payment_vals(self):
        payment_methods = self.payment_type == 'inbound' and self.journal_id.inbound_payment_method_ids \
                          or self.journal_id.outbound_payment_method_ids
        return {
            'partner_id': self.partner_id.id,
            'journal_id': self.journal_id.id,
            'payment_type': self.payment_type,
            'partner_type': 'customer' if self.payment_type == 'inbound' else 'supplier',
            'payment_method_id': payment_methods and payment_methods[0].id or False,
            'amount': self.total,
            'payment_imputation_ids': self._get_imputation_vals_for_payment(),
            'payment_date': self._get_payment_date(),
            'currency_id': self.currency_id.id,
            'advance_amount': self.advance_amount,
        }

    def reconcile_credits(self):
        """
        Imputa los créditos seleccionados.
        """

        # Borramos las imputaciones que no se van a realizar
        self.debit_imputation_line_ids.filtered(lambda x: not x.amount).unlink()
        self.credit_imputation_line_ids.filtered(lambda x: not x.amount).unlink()

        lines_to_concile = self.env['account.move.line']

        for imputation in self.credit_imputation_line_ids:

            company_currency = self.company_id.currency_id

            for line in self.debit_imputation_line_ids.filtered(lambda x: x.move_line_id.account_id):

                line_amount = line.amount

                # Si se imputo el restante, ajustamos el valor para ajustar las imprecisiones de usar 2 decimales
                if round(imputation.amount - imputation.amount_residual_in_payment_currency, ROUND_PRECISION) == 0 and \
                        round(line_amount - imputation.amount, ROUND_PRECISION) == 0:
                    self.debit_imputation_line_ids -= line
                    (line.move_line_id + imputation.move_line_id).reconcile()
                    break

                # En el caso que no sean iguales, uno de los dos debe ser mayor que el otro, agarramos el minimo
                minimun_amount = min(line_amount, imputation.amount)

                line.amount -= minimun_amount
                imputation.amount -= minimun_amount
                imputation_amount = company_currency._convert(
                    minimun_amount, self.currency_id, self.company_id, self._get_payment_date(), round=False
                )

                debit_move = imputation.move_line_id if imputation.move_line_id.debit > 0 else line.move_line_id
                credit_move = imputation.move_line_id if imputation.move_line_id.credit > 0 else line.move_line_id

                lines_to_concile |= line.move_line_id

                # Si no se imputo el total de la factura, creamos una conciliacion parcial
                self.env['account.partial.reconcile'].create({
                    'debit_move_id': debit_move.id,
                    'credit_move_id': credit_move.id,
                    'amount': imputation_amount,
                    'amount_currency': minimun_amount if self.currency_id != company_currency else 0.0,
                    'currency_id': self.currency_id.id if self.currency_id != company_currency else False
                })

                # Si lo imputado es menor que lo restante a imputar, pasamos a la otra imputación,
                # si no, sacamos la factura.
                if imputation.amount > 0:
                    self.debit_imputation_line_ids -= line
                else:
                    break

        lines_to_concile.filtered(lambda l: not l.reconciled).reconcile()
        self.credit_imputation_line_ids.unlink()

    def _validate_payment_imputation(self):
        """ Valida los importes registrados a imputar """
        if self.advance_amount < 0:
            raise ValidationError("El importe a cuenta no puede ser menor a 0.")
        if self.total <= 0:
            raise ValidationError("El importe a pagar debe ser positivo.")
        if self.total != self.amount_to_pay and self.payment_type == 'inbound':
            raise ValidationError("El total a pagar tiene que ser igual al total pagado")

        self._validate_imputation_amounts()

    def _validate_imputation_amounts(self):
        """ Valida que los créditos a imputar no sean mayor que los débitos, por cada cuenta contable a imputar. """
        debit_imputations = self.debit_imputation_line_ids.filtered(lambda x: x.amount)
        credit_imputations = self.credit_imputation_line_ids.filtered(lambda x: x.amount)

        debit_accounts = debit_imputations.mapped('move_line_id').mapped('account_id')
        credit_accounts = credit_imputations.mapped('move_line_id').mapped('account_id')

        if credit_accounts | debit_accounts != debit_accounts:
            raise ValidationError(
                "No se pueden imputar créditos de movimientos que tengan "
                "cuentas contables que no se encuentre en los débitos."
            )

        for account in debit_accounts:
            debits = debit_imputations.filtered(lambda x: x.move_line_id.account_id == account)
            credits = credit_imputations.filtered(lambda x: x.move_line_id.account_id == account)
            if sum(debits.mapped('amount')) < sum(credits.mapped('amount')):
                raise ValidationError(
                    "Los créditos a imputar superan a los débitos para la cuenta contable {}".format(account.name)
                )

    def _get_imputation_vals_for_payment(self):
        payment_imputations = []
        for imputation in self.debit_imputation_line_ids.filtered(lambda x: x.amount):
            payment_imputations.append((0, 0, {
                'move_line_id': imputation.move_line_id.id,
                'concile': imputation.concile,
                'amount': imputation.amount,
                'full_reconcile': imputation.full_reconcile,
            }))

        return payment_imputations

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
