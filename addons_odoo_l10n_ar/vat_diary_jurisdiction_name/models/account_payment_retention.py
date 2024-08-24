# -*- encoding: utf-8 -*-

from odoo import models


class AccountPaymentRetention(models.Model):
    _inherit = 'account.payment.retention'

    def get_vat_diary_dict(self):
        vals = super().get_vat_diary_dict()
        vals.update({
            'fiscal_position': self.partner_id.property_account_position_id.reports_name or vals['fiscal_position'],
        })
        return vals

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
