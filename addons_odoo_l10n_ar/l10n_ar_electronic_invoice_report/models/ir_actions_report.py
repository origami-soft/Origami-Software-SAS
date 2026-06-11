# -*- encoding: utf-8 -*-

from odoo import models


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        if self._is_invoice_report(report_ref):
            moves = self.env['account.move'].browse(res_ids)
            if moves and all(moves.mapped('cae')):
                report_ref = 'l10n_ar_electronic_invoice_report.action_electronic_invoice'
        return super()._render_qweb_pdf(report_ref, res_ids, data)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
