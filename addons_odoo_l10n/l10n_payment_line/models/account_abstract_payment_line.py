# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from ..exceptions import exceptions


class AccountAbstractPaymentLine(models.AbstractModel):
    _name = 'account.abstract.payment.line'
    _description = 'Modelo abstracto de líneas de método de pago'

    payment_id = fields.Many2one('account.payment', string="Pago", ondelete='cascade')
    payment_currency_id = fields.Many2one(related='payment_id.currency_id', store=True)
    journal_id = fields.Many2one(
        'account.journal',
        string="Diario",
        required=True,
        domain="[('company_id', '=', company_id), ('type', 'in', ['cash', 'bank']), ('payment_usage', '!=', 'document_book')]",
        compute='compute_journal',
        readonly=False,
        store=True,
        check_company=True
    )
    currency_id = fields.Many2one('res.currency', string="Moneda", compute='get_journal_currency', store=True)
    rate = fields.Float(string="Cotización", digits=(12, 6))
    amount = fields.Monetary(string="Monto", currency_field="currency_id")
    payment_currency_amount = fields.Monetary(string="Equivalente moneda pago", currency_field="payment_currency_id")
    same_currency_as_payment = fields.Boolean(compute='get_same_currency_as_payment')
    name = fields.Char(string="Nombre")
    company_id = fields.Many2one(
        'res.company',
        string='Compania',
        readonly=True,
        related='payment_id.company_id',
        store=True
    )
    date_abstract_payment = fields.Date(string="Fecha", related='payment_id.date')

    @api.depends('company_id', 'payment_id')
    def compute_journal(self):
        """
        La idea es que haya un campo en la empresa que se llame como la tabla _journal_id para traer los valores
        por defecto. En el caso de que la lineas vengan de un transient_model/wizard, la idea es que la tabla transient tenga el mismo nombre de la 
        tabla pero con el prefijo 'register_' y luego sacarle este prefijo y buscar el campo en la compañia como a la tabla comun.
        """
        for payment_line in self:
            field_name = payment_line._table.replace("register_","")
            if not payment_line.journal_id and not payment_line._origin.journal_id and hasattr(payment_line.company_id,
                                                                                               '{}_journal_id'.format(field_name)):
                payment_line.journal_id = getattr(payment_line.company_id, '{}_journal_id'.format(field_name))
            else:
                payment_line.journal_id = payment_line.journal_id or payment_line._origin.journal_id

    @api.depends('journal_id.currency_id', 'journal_id.company_id.currency_id', 'payment_id.company_id.currency_id')
    def get_journal_currency(self):
        for r in self:
            r.currency_id = r.journal_id.currency_id or r.journal_id.company_id.currency_id if r.journal_id else \
                r.payment_id.company_id.currency_id

    @api.depends('currency_id', 'payment_currency_id')
    def get_same_currency_as_payment(self):
        for r in self:
            r.same_currency_as_payment = r.currency_id == r.payment_currency_id

    @api.onchange('journal_id')
    def onchange_update_rate(self):
        if self.env.context.get('do_not_update_rates'):
            return
        if self.currency_id:
            payment = self.payment_id
            self.rate = self.env['res.currency']._get_conversion_rate(
                payment.currency_id, self.currency_id, payment.company_id, self.date_abstract_payment)
        else:
            self.rate = False

    @api.onchange('amount', 'rate')
    def onchange_amount(self):
        """ Al modificar el monto actualizo el monto en moneda de pago según la tasa de la línea """
        if self.env.context.get('payment_currency_amount_modified'):
            return
        ctx = self.env.context.copy()
        ctx['amount_modified'] = True
        self.env.context = ctx
        self.payment_currency_amount = round(self.amount / self.rate, 2) if self.rate else 0

    @api.onchange('payment_currency_amount')
    def onchange_payment_currency_amount(self):
        """
        Al modificar el monto en moneda de pago actualizo la tasa (siempre y cuando la moneda del método y la del pago
        sean distintas, si son iguales actualizo el monto de la línea)
        """
        if self.env.context.get('amount_modified'):
            return
        ctx = self.env.context.copy()
        ctx['payment_currency_amount_modified'] = True
        self.env.context = ctx
        payment_amount = self.payment_currency_amount
        if self.currency_id != self.payment_currency_id:
            self.rate = self.amount / payment_amount if payment_amount else 0
        else:
            self.amount = payment_amount
    
    def get_line_error_description(self):
        raise NotImplementedError

    def validate_journal_accounts(self):
        for r in self.filtered(lambda l: l.journal_id):
            inbound_payment = r.payment_id.payment_type == 'inbound'
            if inbound_payment and not r.journal_id._get_journal_inbound_outstanding_payment_accounts() \
                    or not (inbound_payment or r.journal_id._get_journal_outbound_outstanding_payment_accounts()):
                return False
        return True

    @api.constrains('journal_id')
    def check_journal_id(self):
        for r in self:
            if not r.validate_journal_accounts():
                exceptions.no_account(r.journal_id.name)

    def validate_amount(self):
        return self.amount > 0

    @api.constrains('amount')
    def check_amount(self):
        for r in self:
            if not r.validate_amount():
                exceptions.invalid_amount(r.get_line_error_description())

    def validate_rate(self):
        return self.rate > 0

    @api.constrains('rate')
    def check_rate(self):
        for r in self:
            if not r.validate_rate():
                exceptions.invalid_rate(r.get_line_error_description())

    def get_payment_currency_field(self, payment):
        return 'payment_currency_id'

    def get_rate_field(self, payment):
        return 'rate'

    def get_amount_field(self, payment):
        return 'payment_currency_amount'

    def get_date_field(self):
        return 'date_abstract_payment'

    def get_line_date(self):
        return getattr(self, self.get_date_field())

    def get_observation(self):
        return 'name'

    def get_line_observation(self):
        return getattr(self, self.get_observation())

    def get_move_lines_amount(self, payment):
        company = payment.company_id
        if self.currency_id == company.currency_id:
            return self.amount
        payment_currency = getattr(self, self.get_payment_currency_field(payment))
        return payment_currency.with_context(fixed_rate=getattr(self, self.get_rate_field(payment)),
                                             fixed_from_currency=payment_currency,
                                             fixed_to_currency=self.currency_id)._convert(
            getattr(self, self.get_amount_field(payment)), company.currency_id, company, payment.date)

    def get_name_for_move_line(self):
        return self.name or self.journal_id.name
    
    def get_first_move_line_name(self):
        return "{} - {}".format(self.payment_id.name, self.get_name_for_move_line())

    def get_first_move_line_amount_currency(self):
        return self.amount

    def get_first_move_line_currency(self, payment):
        return self.currency_id.id

    def get_first_move_line_debit_account(self):
        accounts = self.journal_id._get_journal_inbound_outstanding_payment_accounts()
        return accounts[0].id if accounts else False

    def get_first_move_line_credit_account(self):
        accounts = self.journal_id._get_journal_outbound_outstanding_payment_accounts()
        return accounts[0].id if accounts else False

    def get_second_move_line_amount_currency(self, payment):
        return getattr(self, self.get_amount_field(payment))

    def get_second_move_line_currency(self, payment):
        payment_currency = getattr(self, self.get_payment_currency_field(payment))
        return payment_currency.id

    def get_move_vals(self, payment):
        self.ensure_one()
        inbound_payment = payment.payment_type == 'inbound'
        amount_currency_multiplier = -1 if inbound_payment else 1
        amount = self.get_move_lines_amount(payment)
        return {
            'date': payment.date,
            'ref': payment.ref,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id.id,
            'partner_id': payment.partner_id.id,
            'payment_id': payment.id,
            'line_ids': [
                (0, 0, {
                    'name': self.get_first_move_line_name(),
                    'amount_currency': -self.get_first_move_line_amount_currency() * amount_currency_multiplier,
                    'currency_id': self.get_first_move_line_currency(payment),
                    'credit': 0.0 if inbound_payment else amount,
                    'debit': amount if inbound_payment else 0.0,
                    'date_maturity': payment.date,
                    'partner_id': payment.partner_id.commercial_partner_id.id,
                    'account_id': self.get_first_move_line_debit_account() if inbound_payment \
                        else self.get_first_move_line_credit_account(),
                    'payment_id': payment.id,
                }),
                (0, 0, {
                    'name': payment.get_second_payment_line_move_line_name(),
                    'amount_currency': self.get_second_move_line_amount_currency(payment) * amount_currency_multiplier,
                    'currency_id': self.get_second_move_line_currency(payment),
                    'credit': amount if inbound_payment else 0.0,
                    'debit': 0.0 if inbound_payment else amount,
                    'date_maturity': payment.date,
                    'partner_id': payment.partner_id.commercial_partner_id.id,
                    'account_id': payment.get_journal_debit_account() if inbound_payment \
                        else payment.get_journal_credit_account(),
                    'payment_id': payment.id,
                }),
            ],
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
