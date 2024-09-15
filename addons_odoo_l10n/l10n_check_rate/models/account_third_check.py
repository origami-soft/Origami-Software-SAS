# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from ..exceptions import exceptions


class AccountThirdCheck(models.Model):
    _inherit = 'account.third.check'

    natural_sent_rate = fields.Float(string="Cotización de envío", digits=(12, 6))
    sent_rate = fields.Float(digits=(12, 10))

    def validate_natural_sent_rate(self):
        return all(not r.destination_payment_id or r.natural_sent_rate >= 1 for r in self)
    
    def get_destination_payment(self):
        return self.destination_payment_id or (self.payment_register_ids[0] if self.payment_register_ids else fields.Date.today())
    
    def get_destination_date(self):
        return self.destination_payment_id.date or (self.payment_register_ids[0].payment_date if self.payment_register_ids else False)

    @api.constrains('natural_sent_rate')
    def check_natural_sent_rate(self):
        if not self.validate_natural_sent_rate():
            exceptions.invalid_natural_sent_rate()

    def update_natural_sent_rate(self):
        if not (self.sent_rate and self.currency_id):
            self.natural_sent_rate = 0
            return
        payment = self.get_destination_payment()
        real_rate = self.env['res.currency']._get_conversion_rate(
            payment.currency_id, self.currency_id, payment.company_id, self.get_destination_date())
        self.natural_sent_rate = self.sent_rate if real_rate >= 1 else 1 / self.sent_rate

    @api.onchange('natural_sent_rate')
    def onchange_natural_sent_rate(self):
        if not (self.natural_sent_rate and self.currency_id):
            self.sent_rate = 0
            return
        payment = self.get_destination_payment()
        real_rate = self.env['res.currency']._get_conversion_rate(
            payment.currency_id, self.currency_id, payment.company_id, self.get_destination_date())
        self.sent_rate = self.natural_sent_rate if real_rate >= 1 else 1 / self.natural_sent_rate

    @api.onchange('sent_rate')
    def onchange_sent_rate(self):
        res = super(AccountThirdCheck, self).onchange_sent_rate()
        self.update_natural_sent_rate()
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
