# -*- encoding: utf-8 -*-

from odoo import models, api


class ReportDocumentTax(models.AbstractModel):

    _name = 'report.l10n_ar_perceptions_retentions_pdf.report_document_tax'
    _table = 'report_document_tax'
    _description = 'Reporte de percepciones/retenciones'

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'docs': self.env[data.get('model')].browse(data.get('ids')),
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
