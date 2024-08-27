# -*- encoding: utf-8 -*-

from odoo import models


class AccountAbstractPaymentLine(models.AbstractModel):
    """
    Hacemos estos hooks porque no se puede usar getattr en qweb :|
    """
    _inherit = 'account.abstract.payment.line'

    def get_amount_field_value(self, payment):
        return getattr(self, self.get_amount_field(payment))

    def get_rate_field_value(self, payment):
        return getattr(self, self.get_rate_field(payment))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
