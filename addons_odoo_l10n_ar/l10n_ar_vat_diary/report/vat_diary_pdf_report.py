# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models


class GeneralJournalReport(models.AbstractModel):
    _name = "report.l10n_ar_vat_diary.pdf_vat_diary_report"
    _description = "Reporte PDF Subdiario IVA"

    def _get_report_values(self, docids, data=None):
        docs = self.env['wizard.vat.diary'].browse(data['wizard_id'])
        # Se pasa al reporte una lista con todos los moves para mejorar la
        # eficiencia de memoria en la impresión
        docargs = {
            'doc_ids': data['wizard_id'],
            'doc_model': 'wizard.vat.diary',
            'docs': docs,
            'moves': data['moves']
        }
        return docargs

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
