# -*- encoding: utf-8 -*-

from odoo import models


class AccountPartnerLedger(models.AbstractModel):
    _inherit = 'account.partner.ledger.report.handler'

    def _get_aml_values(self, options, partner_ids, offset=0, limit=None):
        res = super()._get_aml_values(options, partner_ids, offset, limit)
        for partner_id, vals in res.items():
            for dict in vals:
                self.env.cr.execute(f"select full_voucher_name from account_move where id in (select move_id from account_move_line where id = {dict['id']})")
                dict['move_name'] = self.env.cr.fetchone()[0]
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
