# -*- encoding: utf-8 -*-

from odoo import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def get_formatted_vat(self):
        self.ensure_one()
        if self.vat:         
            vat = str(self.vat)
            document_type_code = self.env['codes.models.relation'].get_code(
                'partner.document.type',
                self.partner_document_type_id.id,
                'Afip'
            )
            return vat[:2]+'-'+vat[2:10]+'-'+vat[-1:] if document_type_code in ('80', '86') else vat

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
