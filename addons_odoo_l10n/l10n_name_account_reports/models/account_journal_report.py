# -*- encoding: utf-8 -*-

from odoo import models


class AccountJournalReport(models.AbstractModel):
    _inherit = 'account.journal.report.handler'

    def _get_first_move_line(self, options, parent_key, line_key, values, is_unreconciled_payment):
        res = super()._get_first_move_line(options, parent_key, line_key, values, is_unreconciled_payment)
        if res.get('move_id'):
            self.env.cr.execute(f"select full_voucher_name from account_move where id = {res['move_id']}")
            res['name'] = self.env.cr.fetchone()[0]
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
