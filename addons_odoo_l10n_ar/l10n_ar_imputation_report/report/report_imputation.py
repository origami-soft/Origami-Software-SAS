# -*- encoding: utf-8 -*-

from odoo import models, api
from odoo.exceptions import ValidationError


class ReportImputations(models.AbstractModel):

    _name = 'report.l10n_ar_imputation_report.report_imputation'
    _description = 'Reporte de imputaciones'
    _table = 'report_imputation'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        for move in docs:
            if move.state != 'posted':
                raise ValidationError('No se puede imprimir el reporte de imputaciones de una factura sin confirmar.')

        docargs = {
            'doc_ids': docids,
            'doc_model': self.env['account.move'],
            'docs': docs,
            'previsualize': self.env.context.get('previsualize_invoices')
        }
        return docargs

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
