# -*- encoding: utf-8 -*-

from odoo import models


class GeneralJournalReport(models.AbstractModel):
    _name = "report.l10n_ar_vat_diary.pdf_vat_diary_report"
    _description = "Reporte PDF Subdiario IVA"

    def _get_report_values(self, docids, data=None):
        docs = self.env['vat.diary'].browse(data['diary_id'])
        # Se pasa al reporte una lista con todos los moves para mejorar la
        # eficiencia de memoria en la impresión
        docargs = {
            'doc_ids': data['diary_id'],
            'doc_model': 'vat.diary',
            'docs': docs,
            'moves': data['moves']
        }
        return docargs

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
