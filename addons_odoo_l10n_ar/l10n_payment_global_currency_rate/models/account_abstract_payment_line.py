# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class AccountAbstractPaymentLine(models.AbstractModel):

    _inherit = 'account.abstract.payment.line'

    payment_currency_rate = fields.Float(related='payment_id.currency_rate')
    payment_current_currency_rate = fields.Float(related='payment_id.current_currency_rate')

    def get_rate_field(self, payment):
        """ Como ya no tomamos la cotizacion de la linea, usamos los nuevos campos """
        if self.currency_id == self.company_id.currency_id:
            return super(AccountAbstractPaymentLine, self).get_rate_field(payment)
        return 'payment_currency_rate' if self.payment_currency_rate else 'payment_current_currency_rate'

    @api.onchange('journal_id')
    def onchange_update_rate(self):
        res = super(AccountAbstractPaymentLine, self).onchange_update_rate()
        if self.currency_id == self.company_id.currency_id:
            self.rate = self.payment_currency_rate if self.payment_currency_rate else self.payment_current_currency_rate
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
