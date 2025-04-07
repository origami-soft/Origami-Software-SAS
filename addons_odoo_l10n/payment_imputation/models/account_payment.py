# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
ROUND_PRECISION = 2


class AccountPayment(models.Model):

    _inherit = 'account.payment'

    @api.depends('payment_imputation_ids', 'payment_imputation_ids.full_reconcile',
                 'amount', 'date', 'currency_id', 'payment_type')
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
    writeoff_account_id = fields.Many2one(
        'account.account',
        string="Cuenta de ajuste",
        copy=False,
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]",
        check_company=True
    )
    writeoff_label = fields.Char(
        string='Etiqueta de ajuste',
        default='Ajuste',
        help='Es la etiqueta de la linea del asiento del ajuste'
    )
    payment_difference_handling = fields.Selection([
        ('open', 'Mantener abierto'),
        ('reconcile', 'Marcar como pagado'),
    ], default='open', string="Diferencia en pago")

    @api.depends('is_internal_transfer', 'payment_imputation_ids', 'amount', 'advance_amount')
    def _compute_payment_imputation_difference(self):
        for payment in self:
            if not payment.is_internal_transfer and (payment.payment_imputation_ids or payment.advance_amount):
                total_imputation = sum(payment.payment_imputation_ids.mapped('amount'))
                payment.payment_imputation_difference = payment.amount - payment.advance_amount - total_imputation
            else:
                payment.payment_imputation_difference = 0

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
            lambda r: not r.reconciled and r.account_id.account_type in (
                'liability_payable', 'asset_receivable'
            )
        )
        debit_lines = [(0, 0, {
            'move_line_id': line.id,
            'amount': abs(line.amount_residual),
            'concile': True,
        }) for line in lines]
        if not self.payment_imputation_ids:
            self.payment_imputation_ids = debit_lines

        return rec

    def action_post(self):
        self.check_difference()
        if self.payment_imputation_ids:
            self.reconciled_invoice_ids = None
        self._create_writeoff_line()
        res = super(AccountPayment, self).action_post()
        self.create_imputation()
        return res
    
    def check_difference(self):
        for r in self:
            if r.payment_imputation_difference:
                raise ValidationError("Hay $ {} de diferencia sin asignar.".format('%.2f' % abs(r.payment_imputation_difference)))

    def _create_writeoff_line(self):
        for payment_id in self:
            if payment_id.payment_difference_handling == 'reconcile':
                # Tengo que pasar por contexto que no se valide nada del asiento, porque voy a agregar y eliminar apuntes
                # Lo cual podría dar errores de validación antes de que se llegue a balancear el asiento
                payment_id = payment_id.with_context(check_move_validity=False)
                write_off_vals = payment_id._get_writeoff_line_vals()
                # Contemplo el caso de haber cancelado el pago y volverlo a validar,
                # en tal caso debo regenerar la línea de write-off
                write_off_line = payment_id.line_ids.filtered(
                    lambda l: l.account_id == payment_id.writeoff_account_id
                )
                if write_off_line:
                    write_off_line.unlink()
                # Creo la línea de write-off para el asiento del pago
                payment_id.line_ids = [(0, 0, write_off_vals)]
                # Sincronizo los valores del pago para que ajuste la contraparte del asiento
                payment_id._synchronize_to_moves(changed_fields=['amount'])

    def _get_writeoff_line_vals(self):
        payment_difference_company = self.currency_id._convert(
            self.payment_difference,
            self.company_id.currency_id,
            self.company_id,
            self.date,
        )
        return {
            'name': self.writeoff_label,
            'amount_currency': self.payment_difference,
            'currency_id': self.currency_id.id,
            'debit': payment_difference_company if payment_difference_company > 0.0 else 0.0,
            'credit': -payment_difference_company if payment_difference_company < 0.0 else 0.0,
            'partner_id': self.partner_id.id,
            'account_id': self.writeoff_account_id.id,
            'move_id': self.move_id.id,
        }

    def _get_payment_date(self):
        self.ensure_one()
        return self.date or fields.Date.today()

    @api.constrains('advance_amount')
    def check_advance_amount(self):
        if any(payment.advance_amount < 0 for payment in self):
            raise ValidationError('El importe a cuenta no puede ser negativo.')

    @api.onchange('is_internal_transfer')
    def onchange_reset_advance_amount(self):
        if self.is_internal_transfer:
            self.advance_amount = 0
    
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
        self.reconciled_invoice_ids = self.payment_imputation_ids.mapped('move_line_id').mapped('move_id').filtered(
            lambda x: x.is_invoice()
        )

        # Verificamos los montos de las imputaciones e importe a cuenta contra el del pago
        imp_total = sum(i.amount for i in self.payment_imputation_ids)
        if round(self.amount - self.advance_amount - imp_total, ROUND_PRECISION) != 0:
            raise ValidationError(
                "La cantidad a pagar debe ser igual a la suma de los totales a imputar y el importe a cuenta"
            )

        lines_to_reconcile = move_line

        # Itero las imputaciones, ordenando por lo que quedará pendiente y el monto de la imputación, para evitar
        # problemas con la conciliación de apuntes base
        for imputation in self.payment_imputation_ids.sorted(
                key=lambda l: (l.amount_residual_in_payment_currency - l.amount, -l.amount)
        ):

            amount_currency = False
            imputation_move = imputation.move_line_id.move_id
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

            imputation_date = imputation_move.invoice_date or imputation_move.date or fields.date.today()
            amount = self.currency_id._convert(
                imputation_amount,
                imputation.company_currency_id,
                self.company_id,
                imputation_move._get_accounting_date(imputation_date, False),
                round=False
            )
            # Caso de multimoneda
            if imputation.move_line_id.currency_id:
                amount_currency = self.currency_id._convert(
                    imputation_amount,
                    imputation.move_line_id.currency_id,
                    self.company_id,
                    imputation_move._get_accounting_date(imputation_date, False),
                    round=False
                )
            debit_move = move_line if move_line.debit > 0 else imputation.move_line_id
            credit_move = move_line if move_line.credit > 0 else imputation.move_line_id

            if not (full or imputation.full_reconcile):
                # Para casos parciales aprovechamos los compute storeados
                imputation.move_line_id.update({
                    'amount_residual': amount if self.payment_type == 'inbound' else -amount,
                    'amount_residual_currency': amount_currency if self.payment_type == 'inbound' else -amount_currency
                })
                
                (debit_move | credit_move).reconcile()
                imputation.move_line_id._compute_amount_residual()

            if full or imputation.full_reconcile:
                lines_to_reconcile |= imputation.move_line_id

        lines_to_reconcile.filtered(lambda l: not l.reconciled).reconcile()

    def _get_imputation_move_lines(self):
        account_type = 'asset_receivable' if self.payment_type == 'inbound' else 'liability_payable'
        search_domain = [
            ('account_id.account_type', '=', account_type),
            ('partner_id', '=', self.partner_id.id),
            ('reconciled', '=', False),
            ('amount_residual', '!=', 0.0),
            ('company_id', '=', self.company_id.id),
        ]
        lines = self.env['account.move.line'].search(search_domain) if self.partner_id else \
            self.env['account.move.line']
        return lines.filtered(lambda x: x.debit > 0 if account_type == 'asset_receivable' else x.credit > 0)

    @api.onchange('currency_id')
    def _onchange_currency(self):
        for line in self.payment_imputation_ids:
            line.onchange_concile()

    def create_imputation(self):
        for payment in self:
            if any(inv.state != 'posted'
                   for inv in payment.mapped('payment_imputation_ids').mapped('move_line_id').mapped('move_id')):
                raise ValidationError("Solo se pueden pagar documentos en estado abierto!.")
            if payment.payment_imputation_ids:
                payment.reconcile_imputations(
                    payment.move_id.line_ids.filtered(lambda x: x.account_id == payment.destination_account_id)
                )

    @api.depends('move_id.line_ids.matched_debit_ids', 'move_id.line_ids.matched_credit_ids')
    def _compute_payment_imputation_move_ids(self):
        for record in self:
            """Llamo al método _compute_stat_buttons_from_reconciliation para que deje 
            en el record del payment el campo reconciled_invoice_ids calculado"""
            record._compute_stat_buttons_from_reconciliation()
            record.payment_imputation_move_ids.unlink()
            res = []
            if record.reconciled_invoice_ids:
                res.extend(
                    [(0, 0, {'move_id': move.id, 'payment_id': record.id}) for move in record.reconciled_invoice_ids])
            if record.reconciled_bill_ids:
                res.extend(
                    [(0, 0, {'move_id': move.id, 'payment_id': record.id}) for move in record.reconciled_bill_ids])
            record.payment_imputation_move_ids = res

    @api.depends('reconciled_invoice_ids', 'payment_type', 'partner_type', 'partner_id', 'payment_imputation_ids')
    def _compute_destination_account_id(self):
        """ Heredo el método para mantener la funcionalidad estándar 
        de utilizar la cuenta deudora o acreedora de las facturas 
        como cuenta de destino, pero aplicandolo a líneas de imputación"""
        super(AccountPayment, self)._compute_destination_account_id()
        for payment in self:
            if payment.payment_imputation_ids:
                payment.destination_account_id = payment.payment_imputation_ids.mapped('move_line_id.account_id').filtered(
                                                 lambda account: account.account_type in ('asset_receivable', 'liability_payable'))[0]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
