# -*- encoding: utf-8 -*-

from odoo import models


class AccountGeneralLedgeReport(models.AbstractModel):
    _inherit = 'account.general.ledger.report.handler'

    def _get_aml_line(self, report, parent_line_id, options, eval_dict, init_bal_by_col_group):
        res = super()._get_aml_line(report, parent_line_id, options, eval_dict, init_bal_by_col_group)
        if res['caret_options'] == 'account.move.line':
            aml_id = int(res['id'].split('account.move.line~')[1])
            self.env.cr.execute(f"select full_voucher_name from account_move where id in (select move_id from account_move_line where id = {aml_id})")
            res['name'] = self.env.cr.fetchone()[0]
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
