# -*- encoding: utf-8 -*-

from odoo import models


class AccountFollowupReport(models.AbstractModel):
    _inherit = 'account.followup.report'

    def _get_followup_report_lines(self, options):
        res = super()._get_followup_report_lines(options)
        for line in res:
            move_id = line.get('account_move', False)
            if move_id:
                line['name'] = move_id.full_voucher_name or move_id.name
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
