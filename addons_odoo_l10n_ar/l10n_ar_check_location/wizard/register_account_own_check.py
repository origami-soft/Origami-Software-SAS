# -*- encoding: utf-8 -*-

from odoo import models


class RegisterAccountOwnCheck(models.TransientModel):
    _inherit = 'register.account.own.check'

    def get_payment_line_vals(self):
        res = super().get_payment_line_vals()
        res.update({
            'check_location_id': self.check_location_id.id,
        })
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
