# -*- encoding: utf-8 -*-

from odoo import models


class RegisterAccountAbstractPaymentLine(models.AbstractModel):
    _inherit = "register.account.abstract.payment.line"

    def get_payment_line_vals(self):
        vals = super().get_payment_line_vals()
        if self.natural_rate:
            vals['natural_rate'] = self.natural_rate
        return vals

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
