# -*- encoding: utf-8 -*-

from odoo import models, api


class ElectronicInvoice(models.AbstractModel):
    _name = 'report.l10n_ar_electronic_invoice_report.electronic_invoice'
    _description = 'Reporte de factura electrónica'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)

        # En caso de que se esté previsualizando una factura o editando el reporte con Studio, no corro las validaciones
        if not any(self.env.context.get(k) for k in ['previsualize_invoices', 'studio']):
            for doc in docs:
                doc.validate_electronic_invoice_fields()

        docargs = {
            'doc_ids': docids,
            'doc_model': self.env['account.move'],
            'docs': docs,
            'previsualize': self.env.context.get('previsualize_invoices')
        }
        return docargs

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
