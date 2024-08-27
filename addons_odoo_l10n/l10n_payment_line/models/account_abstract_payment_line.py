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
from ..exceptions.exceptions import NoAccountError, InvalidAmountError, InvalidRateError


class AccountAbstractPaymentLine(models.AbstractModel):
    _name = 'account.abstract.payment.line'
    _description = 'Modelo abstracto de líneas de método de pago'

    payment_id = fields.Many2one('account.payment', string="Pago", ondelete='cascade')
    payment_currency_id = fields.Many2one(related='payment_id.currency_id', store=True)
    journal_id = fields.Many2one(
        'account.journal',
        string="Diario",
        required=True,
        domain="[('company_id', '=', company_id), ('type', 'in', ['cash', 'bank']), ('multiple_payment_journal', '=', False)]",
        compute='compute_journal',
        readonly=False,
        store=True,
        check_company=True
    )
    currency_id = fields.Many2one('res.currency', string="Moneda", compute='get_journal_currency', store=True)
    rate = fields.Float(string="Cotización", digits=(12, 6))
    amount = fields.Float(string="Monto")
    payment_currency_amount = fields.Float(string="Monto en moneda de pago")
    same_currency_as_payment = fields.Boolean(compute='get_same_currency_as_payment')
    name = fields.Char(string="Nombre")
    company_id = fields.Many2one(
        'res.company',
        string='Compania',
        readonly=True,
        related='payment_id.company_id',
        store=True
    )
    date_abstract_payment = fields.Date(string="Fecha", related='payment_id.payment_date')

    @api.depends('company_id', 'payment_id')
    def compute_journal(self):
        """
        La idea es que haya un campo en la empresa que se llame como la tabla _journal_id para traer los valores
        por defecto.
        """
        for payment_line in self:
            if not payment_line.journal_id and not payment_line._origin.journal_id and hasattr(payment_line.company_id,
                                                                                               '{}_journal_id'.format(
                                                                                                       payment_line._table)):
                payment_line.journal_id = getattr(payment_line.company_id, '{}_journal_id'.format(payment_line._table))
            else:
                payment_line.journal_id = payment_line.journal_id or payment_line._origin.journal_id

    @api.depends('journal_id.currency_id', 'payment_id.company_id.currency_id')
    def get_journal_currency(self):
        for r in self:
            company_currency = r.payment_id.company_id.currency_id
            currency = r.journal_id.currency_id or company_currency if r.journal_id else False
            r.currency_id = currency

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
                payment.currency_id, self.currency_id, payment.company_id, payment.payment_date)
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

    def validate_journal_accounts(self):
        for r in self.filtered(lambda l: l.journal_id):
            inbound_payment = r.payment_id.payment_type not in ('outbound', 'transfer')
            if inbound_payment and not r.journal_id.default_debit_account_id \
                    or not (inbound_payment or r.journal_id.default_credit_account_id):
                return False
        return True

    @api.constrains('journal_id')
    def check_journal_id(self):
        if not self.validate_journal_accounts():
            raise NoAccountError(
                "El diario seleccionado como método de pago no posee la cuenta contable por defecto correspondiente.")

    def validate_amount(self):
        return all(r.amount > 0 for r in self)

    @api.constrains('amount')
    def check_amount(self):
        if not self.validate_amount():
            raise InvalidAmountError("El monto de la línea debe ser positivo.")

    def validate_rate(self):
        return all(r.rate > 0 for r in self)

    @api.constrains('rate')
    def check_rate(self):
        if not self.validate_rate():
            raise InvalidRateError("La cotización de la línea debe ser positiva.")

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
        if self.currency_id == payment_currency:
            return payment_currency._convert(
                getattr(self, self.get_amount_field(payment)), company.currency_id, company, payment.payment_date)
        return payment_currency.with_context(fixed_rate=getattr(self, self.get_rate_field(payment)),
                                             fixed_from_currency=payment_currency,
                                             fixed_to_currency=self.currency_id)._convert(
            getattr(self, self.get_amount_field(payment)), company.currency_id, company, payment.payment_date)

    def get_first_move_line_name(self):
        return self.name or self.journal_id.name

    def get_first_move_line_amount_currency(self, payment):
        return self.amount if self.currency_id != payment.company_id.currency_id else 0.0

    def get_first_move_line_currency(self, payment):
        return self.currency_id.id if self.currency_id != payment.company_id.currency_id else False

    def get_first_move_line_debit_account(self):
        return self.journal_id.default_debit_account_id.id

    def get_first_move_line_credit_account(self):
        return self.journal_id.default_credit_account_id.id

    def get_second_move_line_amount_currency(self, payment):
        return getattr(self, self.get_amount_field(payment)) if getattr(self, self.get_payment_currency_field(payment)) \
                                                                != payment.company_id.currency_id else 0.0

    def get_second_move_line_currency(self, payment):
        payment_currency = getattr(self, self.get_payment_currency_field(payment))
        return payment_currency.id if payment_currency != payment.company_id.currency_id else False

    def get_move_vals(self, payment):
        self.ensure_one()
        inbound_payment = payment.payment_type not in ('outbound', 'transfer')
        amount_currency_multiplier = -1 if inbound_payment else 1
        amount = self.get_move_lines_amount(payment)
        return {
            'date': payment.payment_date,
            'ref': payment.communication,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id.id,
            'partner_id': payment.partner_id.id,
            'line_ids': [
                (0, 0, {
                    'name': self.get_first_move_line_name(),
                    'amount_currency': -self.get_first_move_line_amount_currency(payment) * amount_currency_multiplier,
                    'currency_id': self.get_first_move_line_currency(payment),
                    'credit': 0.0 if inbound_payment else amount,
                    'debit': amount if inbound_payment else 0.0,
                    'date_maturity': payment.payment_date,
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
                    'date_maturity': payment.payment_date,
                    'partner_id': payment.partner_id.commercial_partner_id.id,
                    'account_id': payment.get_journal_debit_account() if inbound_payment \
                        else payment.get_journal_credit_account(),
                    'payment_id': payment.id,
                }),
            ],
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
