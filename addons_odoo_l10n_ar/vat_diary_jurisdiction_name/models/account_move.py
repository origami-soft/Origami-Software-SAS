# -*- encoding: utf-8 -*-

from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def get_vat_diary_dict(self):
        vals = super().get_vat_diary_dict()
        jurisdiction = self.jurisdiction_id or self.partner_id.state_id
        vals.update({
            'fiscal_position': self.fiscal_position_id.reports_name or vals['fiscal_position'],
            'jurisdiction': jurisdiction.reports_name or jurisdiction.name or '',
        })
        return vals

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
