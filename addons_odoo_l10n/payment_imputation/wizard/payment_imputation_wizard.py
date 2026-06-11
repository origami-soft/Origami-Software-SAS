# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare, float_round

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

    partner_id = fields.Many2one(
        'res.partner',
        'Partner',
        required=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id
    )
    payment_type = fields.Selection(
        [('inbound', 'Inbound'), ('outbound', 'Outbound')],
        'Tipo'
    )
    advance_amount = fields.Float(
        'Importe a cuenta'
    )
    journal_id = fields.Many2one(
        'account.journal',
        domain=lambda l: [('type', 'in', ('bank', 'cash')), ("company_id", "=", l.env.company.id)],
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
    total = fields.Float(
        'Total',
        compute=_get_total_payment
    )
    date = fields.Date(
        'Fecha'
    )
    amount_to_pay = fields.Float(
        string='Total a pagar'
    )
    amount_left = fields.Float(
        string='Faltante a pagar',
        compute="_compute_amount_left"
    )
    company_id = fields.Many2one(
        'res.company',
        default=lambda x: x.env.company.id,
    )
    operation_type = fields.Selection(
        [('payment', 'Pago'), ('conciliation', 'Conciliación')],
        string='Tipo de operación',
        default='payment'
    )

    select_all_debit = fields.Boolean('Seleccionar todos los débitos')
    select_all_credit = fields.Boolean('Seleccionar todos los créditos')
    
    # Campos para conciliación
    subtotal_debit = fields.Float(
        string='Sub-total débitos',
        compute='_compute_subtotals'
    )
    subtotal_credit = fields.Float(
        string='Sub-total créditos', 
        compute='_compute_subtotals'
    )
    difference = fields.Float(
        string='Diferencia',
        compute='_compute_subtotals'
    )

    @api.depends('debit_imputation_line_ids.amount', 'credit_imputation_line_ids.amount')
    def _compute_subtotals(self):
        for record in self:
            record.subtotal_debit = sum(record.debit_imputation_line_ids.mapped('amount'))
            record.subtotal_credit = sum(record.credit_imputation_line_ids.mapped('amount'))
            record.difference = record.subtotal_debit - record.subtotal_credit

    def get_journal_domain(self):
        return [('type', 'in', ('bank', 'cash')), ('company_id', '=', self.env.company.id)]

    @api.model
    def default_get(self, fields_list):
        res = super(PaymentImputationWizard, self).default_get(fields_list)
        res['journal_id'] = self.env['account.journal'].search(self.get_journal_domain(), limit=1).id
        return res

    @api.depends('amount_to_pay', 'total')
    def _compute_amount_left(self):
        self.amount_left = self.amount_to_pay - self.total

    @api.constrains('amount_to_pay')
    def _constrain_amount_to_pay(self):
        self.ensure_one()
        if self.amount_to_pay <= 0 and self.payment_type == 'inbound' and self.operation_type == 'payment':
            raise ValidationError("El total a pagar tiene que ser mayor a 0")

    def _get_payment_date(self):
        self.ensure_one()
        return self.date or fields.Date.today()

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        currency = self.currency_id or self.env.company.currency_id
        self.update({
            'debit_imputation_line_ids': None,
            'credit_imputation_line_ids': None,
        })
        lines = self._get_move_lines(currency.id) if self.partner_id and self.currency_id else None
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
            ('account_id.account_type', '=', account_type),
            ('partner_id', '=', self.partner_id.id),
            ('reconciled', '=', False),
            ('currency_id', '=', currency_id),
            ('parent_state', '=', 'posted'),
            ('company_id', '=', self.company_id.id),
            '|',
            ('amount_residual', '!=', 0.0),
            ('amount_residual_currency', '!=', 0.0)
        ]
        return domain

    def _get_move_lines(self, currency_id=None):
        if not (self.partner_id and self.currency_id):
            return {}
        account_type = 'asset_receivable' if self.payment_type == 'inbound' else 'liability_payable'
        search_domain = self._get_move_lines_domain(account_type, currency_id)

        lines = self.env['account.move.line'].search(search_domain)

        # Filtrar líneas con residual cero usando is_zero para evitar problemas de redondeo,
        # Esto previene que aparezcan anticipos o créditos totalmente imputados,
        currency = self.env['res.currency'].browse(currency_id)
        company_currency = self.company_id.currency_id

        lines = lines.filtered(lambda line: 
            not currency.is_zero(line.amount_residual_currency) if line.amount_currency 
            else not company_currency.is_zero(line.amount_residual)
        )
        
        return {
            'debit_lines':  lines.filtered(lambda x: x.debit > 0 if account_type == 'asset_receivable' else x.credit > 0),
            'credit_lines': lines.filtered(lambda x: x.credit > 0 if account_type == 'asset_receivable' else x.debit > 0)
        }

    @api.onchange('journal_id')
    def onchange_journal_id(self):
        if self.journal_id:
            self.currency_id = self.journal_id.currency_id or self.journal_id.company_id.currency_id
            self.onchange_partner_id()
            for l in self.debit_imputation_line_ids:
                l._get_payment_amounts()
                l.onchange_concile()
            for l in self.credit_imputation_line_ids:
                l._get_payment_amounts()
                l.onchange_concile()

    @api.onchange('currency_id')
    def onchange_currency_id(self):
        if self.currency_id:
            self.onchange_partner_id()
            for l in self.debit_imputation_line_ids:
                l._get_payment_amounts()
                l.onchange_concile()
            for l in self.credit_imputation_line_ids:
                l._get_payment_amounts()
                l.onchange_concile()

    def create_payment(self):
        self._validate_payment_imputation()
        move_line = self.env['account.move.line']
        move_line |= self.credit_imputation_line_ids.filtered(lambda x: x.amount).mapped('move_line_id')
        move_line |= self.debit_imputation_line_ids.filtered(lambda x: x.amount).mapped('move_line_id')
        self.reconcile_credits()
        
        if self.operation_type == 'payment':
            self.debit_imputation_line_ids.check_imputation_amount()
            payment = self.env['account.payment'].create(self._get_payment_vals())

            return {
                'name': 'Pago',
                'views': [[False, "form"], [False, "tree"]],
                'res_model': 'account.payment',
                'type': 'ir.actions.act_window',
                'res_id': payment.id,
            }
        else:
            return {
                'name': 'Asientos conciliados',
                'view_mode': 'tree',
                'res_model': 'account.move',
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', move_line.move_id.ids)],
            }

    def _get_payment_vals(self):
        payment_methods = self.payment_type == 'inbound' and \
            self.journal_id.inbound_payment_method_line_ids.mapped('payment_method_id') \
            or self.journal_id.outbound_payment_method_line_ids.mapped('payment_method_id')

        return {
            'partner_id': self.partner_id.id,
            'journal_id': self.journal_id.id,
            'payment_type': self.payment_type or 'outbound',
            'partner_type': 'customer' if self.payment_type == 'inbound' else 'supplier',
            'payment_method_id': payment_methods and payment_methods[0].id or False,
            'amount': self.total,
            'payment_imputation_ids': self._get_imputation_vals_for_payment(),
            'date': self._get_payment_date(),
            'currency_id': self.currency_id.id,
            'advance_amount': self.advance_amount,
        }

    def reconcile_credits(self):
        """
        Imputa los créditos seleccionados.
        """
        precision_digits = self.currency_id.decimal_places
        # Borramos las imputaciones que no se van a realizar
        self.debit_imputation_line_ids.filtered(lambda x: not x.amount).unlink()
        self.credit_imputation_line_ids.filtered(lambda x: not x.amount).unlink()

        for credit_imp in self.credit_imputation_line_ids:
            for debit_imp in self.debit_imputation_line_ids.filtered(lambda x: x.move_line_id.account_id):
                # En caso de que la imputación no tenga importe (porque ya se terminó de conciliar) la ignoro
                if not (credit_imp.amount and debit_imp.amount):
                    continue

                # En caso de que haya que realizar una conciliación parcial, a diferencia de los casos de arriba, tomo
                # el importe mínimo entre el débito y crédito actuales
                if float_compare(debit_imp.amount, credit_imp.amount, precision_digits=precision_digits) == -1:
                    min_amount, rate = debit_imp.amount, debit_imp.move_line_id.get_move_line_rate()
                else:
                    min_amount, rate = credit_imp.amount, credit_imp.move_line_id.get_move_line_rate()

                # Descuento lo que voy a conciliar de los importes actuales del débito y crédito
                debit_imp.amount -= min_amount
                credit_imp.amount -= min_amount

                # Genero la conciliación parcial entre el débito y el crédito por el mínimo obtenido anteriormente
                debit_move = credit_imp.move_line_id if credit_imp.move_line_id.debit > 0 else debit_imp.move_line_id
                credit_move = credit_imp.move_line_id if credit_imp.move_line_id.credit > 0 else debit_imp.move_line_id
                self.env['account.move.line'].do_partial_reconcile_with_exchange_difference(
                    debit_move, credit_move, min_amount)

    def _validate_payment_imputation(self):
        """ Valida los importes registrados a imputar """
        if self.operation_type == 'payment':
            if self.advance_amount < 0:
                raise ValidationError("El importe a cuenta no puede ser menor a 0.")
            if self.total <= 0:
                raise ValidationError("El importe a pagar debe ser positivo.")
            if self.total != self.amount_to_pay and self.payment_type == 'inbound':
                raise ValidationError("El total a pagar tiene que ser igual al total pagado")
        self._validate_imputation_amounts()

    def _validate_imputation_amounts(self):
        """ Valida que los créditos a imputar no sean mayor que los débitos,
        por cada cuenta contable a imputar. """
        precision_digits = self.currency_id.decimal_places
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
            debit_imps = debit_imputations.filtered(lambda x: x.move_line_id.account_id == account)
            credit_imps = credit_imputations.filtered(lambda x: x.move_line_id.account_id == account)
            if float_compare(
                sum(debit_imps.mapped('amount')),
                sum(credit_imps.mapped('amount')),
                precision_digits=precision_digits
            ) == -1:
                raise ValidationError(
                    "Los créditos a imputar superan a los débitos para la cuenta contable {}".format(account.name)
                )
            if float_compare(
                sum(debit_imps.mapped('amount')),
                sum(credit_imps.mapped('amount')),
                precision_digits=precision_digits
            ) == 1 and self.operation_type != 'payment':
                raise ValidationError(
                    "Los débitos a imputar superan a los créditos para la cuenta contable {}".format(account.name)
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

    @api.onchange('select_all_debit')
    def onchange_select_all_debit(self):
        if self.select_all_debit:
            for line in self.debit_imputation_line_ids:
                line.concile = True
                line.amount = line.amount_residual_in_payment_currency
            self._get_total_payment()
            self.select_all_debit = False

    @api.onchange('select_all_credit')
    def onchange_select_all_credit(self):
        if self.select_all_credit:
            for line in self.credit_imputation_line_ids:
                line.concile = True
                line.amount = line.amount_residual_in_payment_currency
            self._get_total_payment()
            self.select_all_credit = False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
