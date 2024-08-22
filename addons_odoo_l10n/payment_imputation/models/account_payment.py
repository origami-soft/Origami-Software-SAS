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


class AccountPayment(models.Model):

    _inherit = 'account.payment'

    @api.depends('payment_imputation_ids', 'payment_imputation_ids.full_reconcile',
                 'amount', 'payment_date', 'currency_id', 'payment_type')
    def _compute_payment_difference(self):
        draft_payments = self.filtered(lambda p: p.state == 'draft')
        for pay in draft_payments:
            difference = sum(
                debit_line.amount_residual_in_payment_currency - debit_line.amount
                for debit_line in pay.payment_imputation_ids.filtered(lambda x: x.full_reconcile)
            )
            pay.payment_difference = -difference if pay.payment_type == 'outbound' else difference
        (self - draft_payments).payment_difference = 0

    payment_difference = fields.Monetary(compute='_compute_payment_difference', readonly=True)

    @api.depends('payment_imputation_ids', 'amount', 'advance_amount')
    def _compute_payment_imputation_difference(self):
        for payment in self:
            total_imputation = sum(payment.payment_imputation_ids.mapped('amount'))
            payment.payment_imputation_difference = payment.amount - payment.advance_amount - total_imputation

    payment_imputation_ids = fields.One2many(
        'payment.imputation.line',
        'payment_id',
        'Imputaciones',
        copy=False
    )
    payment_imputation_move_ids = fields.One2many(
        comodel_name='payment.imputation.move',
        inverse_name='payment_id',
        string='Documentos Imputados',
        compute="_compute_payment_imputation_move_ids",
        store=True,
    )
    payment_imputation_difference = fields.Monetary(
        compute='_compute_payment_imputation_difference',
        string='Diferencia',
        help='La resta del total del pago con las imputaciones y el importe a cuenta',
        readonly=True,
    )
    advance_amount = fields.Monetary(
        'A pagar a cuenta',
        readonly=True
    )

    @api.model
    def default_get(self, fields):
        """ Creamos las imputaciones si por contexto hay facturas desde cualquier vista """
        rec = super(AccountPayment, self).default_get(fields)
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        active_model = self._context.get('active_model')
        if not active_ids or active_model != 'account.move':
            return rec
        lines = self.env['account.move'].browse(active_ids).mapped('line_ids').filtered(
            lambda r: not r.reconciled and r.account_id.internal_type in ('payable', 'receivable')
        )
        debit_lines = [(0, 0, {
            'move_line_id': line.id,
            'amount': abs(line.amount_residual),
            'concile': True,
        }) for line in lines]
        if not self.payment_imputation_ids:
            self.payment_imputation_ids = debit_lines

        return rec

    def post(self):
        if self.payment_imputation_ids:
            self.invoice_ids = None
        res = super(AccountPayment, self).post()
        self.create_imputation()
        return res

    def _get_payment_date(self):
        self.ensure_one()
        return self.payment_date or fields.Date.today()

    @api.constrains('advance_amount')
    def check_advance_amount(self):
        if any(payment.advance_amount < 0 for payment in self):
            raise ValidationError('El importe a cuenta no puede ser negativo.')

    @api.onchange('partner_id')
    def onchange_partner_imputation(self):
        # Si por contexto hay facturas, se crean desde default_get()
        if not self.env.context.get('active_ids'):
            self._get_imputation_move_lines()

    def reconcile_imputations(self, move_line):
        """
        Imputa los importes del pago a las move lines en base a los importes seleccionado en las imputaciones
        :param move_line: account.move.line generada del pago
        """
        # Borramos las imputaciones que no se van a realizar
        self.payment_imputation_ids.filtered(lambda x: not (x.amount or x.full_reconcile)).unlink()

        # Asignamos las facturas al pago
        self.invoice_ids = self.payment_imputation_ids.mapped('move_line_id').mapped('move_id').filtered(
            lambda x: x.is_invoice()
        )

        # Verificamos los montos de las imputaciones e importe a cuenta contra el del pago
        imp_total = sum(i.amount for i in self.payment_imputation_ids)
        if round(self.amount - self.advance_amount - imp_total, ROUND_PRECISION) != 0:
            raise ValidationError(
                "La cantidad a pagar debe ser igual a la suma de los totales a imputar y el importe a cuenta")

        lines_to_reconcile = move_line

        # Itero las imputaciones, ordenando por lo que quedará pendiente y el monto de la imputación, para evitar
        # problemas con la conciliación de apuntes base
        for imputation in self.payment_imputation_ids.sorted(
                key=lambda l: (l.amount_residual_in_payment_currency - l.amount, -l.amount)
        ):

            amount_currency = False
            currency = False

            # Validamos que no haya importes o move lines erróneas
            imputation.validate(imputation.move_line_id)
            # Si se imputó el restante de factura, ajustamos el valor para ajustar las imprecisiones de usar 2 decimales
            full = round(imputation.amount_residual_in_payment_currency - imputation.amount, ROUND_PRECISION) == 0
            if full and self.currency_id != imputation.currency_id:
                imputation_amount = imputation.company_currency_id._convert(
                    imputation.amount_residual_company, self.currency_id, self.company_id, self._get_payment_date(),
                    round=False
                )
            else:
                imputation_amount = min(abs(imputation.amount_residual_in_payment_currency), abs(imputation.amount))

            amount = self.currency_id._convert(
                imputation_amount, imputation.company_currency_id, self.company_id, self._get_payment_date(),
                round=False
            )
            # Caso de multimoneda
            if imputation.move_line_id.currency_id:
                currency = imputation.move_line_id.currency_id
                amount_currency = self.currency_id._convert(
                    imputation_amount, imputation.move_line_id.currency_id, self.company_id, self._get_payment_date(),
                    round=False
                )

            debit_move = move_line if move_line.debit > 0 else imputation.move_line_id
            credit_move = move_line if move_line.credit > 0 else imputation.move_line_id

            # Si no se imputó el total de la factura ni se definió una cuenta destino, creamos una conciliación parcial
            if not (full or imputation.full_reconcile) or self.advance_amount:
                self.env['account.partial.reconcile'].create({
                    'debit_move_id': debit_move.id,
                    'credit_move_id': credit_move.id,
                    'amount': amount,
                    'amount_currency': amount_currency,
                    'currency_id': currency.id if currency else currency,
                })

            # Si no se imputó el total de la factura no nos interesa hacer esta conciliación,
            # con el partial reconcile alcanza
            if full or imputation.full_reconcile:
                lines_to_reconcile |= imputation.move_line_id

        lines_to_reconcile.filtered(lambda l: not l.reconciled).reconcile()

    def _get_imputation_move_lines(self):
        account_type = 'receivable' if self.payment_type == 'inbound' else 'payable'
        search_domain = [
            ('account_id.user_type_id.type', '=', account_type),
            ('partner_id', '=', self.partner_id.id),
            ('reconciled', '=', False),
            ('amount_residual', '!=', 0.0),
            ('company_id', '=', self.company_id.id),
        ]
        lines = self.env['account.move.line'].search(search_domain) if self.partner_id else \
            self.env['account.move.line']
        return lines.filtered(lambda x: x.debit > 0 if account_type == 'receivable' else x.credit > 0)

    @api.onchange('currency_id')
    def _onchange_currency(self):
        super(AccountPayment, self)._onchange_currency()
        for line in self.payment_imputation_ids:
            line.onchange_concile()

    def create_imputation(self):
        for payment in self:
            if any(inv.state != 'posted'
                   for inv in payment.mapped('payment_imputation_ids').mapped('move_line_id').mapped('move_id')):
                raise ValidationError("Solo se pueden pagar documentos en estado abierto!.")
            if payment.payment_imputation_ids:
                payment.reconcile_imputations(
                    payment.move_line_ids.filtered(lambda x: x.account_id == payment.destination_account_id)
                )
    
    @api.depends('move_line_ids.matched_debit_ids', 'move_line_ids.matched_credit_ids')
    def _compute_payment_imputation_move_ids(self):
        for record in self:
            """Llamo al método _compute_reconciled_invoice_ids para que deje 
            en el record del payment el campo reconciled_invoice_ids calculado"""
            record._compute_reconciled_invoice_ids()
            record.payment_imputation_move_ids.unlink()
            if record.reconciled_invoice_ids:
                record.payment_imputation_move_ids = [(0,0,{'move_id': move.id,
                                                            'payment_id': record.id}) 
                                                     for move in record.reconciled_invoice_ids]

    @api.depends('invoice_ids', 'payment_type', 'partner_type', 'partner_id', 'payment_imputation_ids')
    def _compute_destination_account_id(self):
        """ Heredo el método para mantener la funcionalidad estándar 
        de utilizar la cuenta deudora o acreedora de las facturas 
        como cuenta de destino, pero aplicandolo a líneas de imputación"""
        super(AccountPayment, self)._compute_destination_account_id()
        for payment in self:
            if payment.payment_imputation_ids:
                payment.destination_account_id = payment.payment_imputation_ids.mapped('move_line_id.account_id').filtered(
                                                 lambda account: account.user_type_id.type in ('receivable', 'payable'))[0]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
