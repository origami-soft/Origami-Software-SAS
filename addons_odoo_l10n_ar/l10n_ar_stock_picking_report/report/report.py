# -*- encoding: utf-8 -*-

from odoo import models, api


class ReportSelfprintPicking(models.AbstractModel):

    _name = 'report.l10n_ar_stock_picking_report.report_selfprint_layout'
    _description = 'Reporte de remito autoimpresor'
    _table = 'report_selfprint_layout'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['stock.picking'].browse(docids)

        for doc in docs:
            doc.validate_selfprint_fields()

        docargs = {
            'doc_ids': docids,
            'doc_model': self.env['stock.picking'],
            'docs': docs,
        }
        return docargs

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
