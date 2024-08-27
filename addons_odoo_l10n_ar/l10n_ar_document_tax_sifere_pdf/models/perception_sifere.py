# -*- encoding: utf-8 -*-

from odoo import models, api


class PerceptionSifere(models.Model):
    _inherit = 'perception.sifere'

    def generate_pdf(self):
        report_name = 'l10n_ar_perceptions_retentions_pdf.document_tax_report'
        sicore = self.browse(self.ids)
        datas = {
            'ids': self.ids,
            'model': 'perception.sifere',
            'form': sicore
        }
        return self.env.ref(report_name).report_action(None, data=datas)

    def get_report_document_tax_data(self):
        return self.search_records().get_report_document_tax_data()

    def get_report_document_tax_name(self):
        return 'Listado de Percepciones de IIBB Sufridas desde el {} hasta el {}'.format(
            self.date_from.strftime('%d/%m/%Y'),
            self.date_to.strftime('%d/%m/%Y')
        )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
