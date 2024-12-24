# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from ..exceptions import exceptions


class AccountAbstractPaymentLine(models.AbstractModel):
    _inherit = 'account.abstract.payment.line'

    natural_rate = fields.Float(string="Cotización", digits=(12, 6))
    rate = fields.Float(digits=(12, 10))

    def validate_natural_rate(self):
        return all(r.natural_rate >= 1 for r in self)

    @api.constrains('natural_rate')
    def check_natural_rate(self):
        if not self.validate_natural_rate():
            exceptions.invalid_natural_rate_error()

    def update_natural_rate(self):
        if not (self.rate and self.currency_id):
            self.natural_rate = 0
            return
        payment = self.payment_id
        real_rate = self.env['res.currency']._get_conversion_rate(
            payment.currency_id, self.currency_id, payment.company_id, self.date_abstract_payment)
        self.natural_rate = self.rate if real_rate >= 1 else 1 / self.rate

    @api.onchange('natural_rate')
    def onchange_natural_rate(self):
        if not (self.natural_rate and self.currency_id):
            self.rate = 0
            return
        payment = self.payment_id
        real_rate = self.env['res.currency']._get_conversion_rate(
            payment.currency_id, self.currency_id, payment.company_id, payment.date)
        self.rate = self.natural_rate if real_rate >= 1 else 1 / self.natural_rate

    @api.onchange('journal_id')
    def onchange_update_rate(self):
        res = super(AccountAbstractPaymentLine, self).onchange_update_rate()
        self.update_natural_rate()
        return res

    @api.onchange('amount', 'rate')
    def onchange_amount(self):
        res = super(AccountAbstractPaymentLine, self).onchange_amount()
        self.update_natural_rate()
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
