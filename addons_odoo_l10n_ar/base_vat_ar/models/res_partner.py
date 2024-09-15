# -*- encoding: utf-8 -*-

from odoo import models
from l10n_ar_api.padron import contributor


class ResPartner(models.Model):

    _inherit = 'res.partner'

    def check_vat_ar(self, vat_number):
        """
        Verifica que el numero de documento sea correcto para su posicion fiscal
        :param vat_number: str - Numero de documento a validar
        """
        if vat_number and self.partner_document_type_id.verification_required:
            return contributor.Contributor.is_valid_cuit(vat_number)
        return True
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
