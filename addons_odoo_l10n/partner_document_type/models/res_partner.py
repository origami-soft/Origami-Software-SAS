# -*- encoding: utf-8 -*-

import re

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_document_type_id = fields.Many2one(
        comodel_name='partner.document.type',
        string='Tipo de documento',
        ondelete='restrict'
    )
    address_required = fields.Boolean(related='partner_document_type_id.address_required')
     
    @api.constrains("vat", "partner_document_type_id", "country_id", "parent_id")
    def check_vat(self):
        # Si la empresa tiene el mismo pais, obviamos la parte de que el documento
        # necesite el prefijo del pais adelante para el chequeo de documento
        for partner in self:
            country = partner.parent_id.country_id if partner.parent_id else partner.country_id
            if country.not_validate_vat:
                continue
            if country.no_prefix:
                if partner.vat and not re.match("^[a-zA-Z0-9]*$", partner.vat):
                    raise ValidationError("El documento debe poseer solamente numeros y letras")
                check_func = partner.simple_vat_check
                if partner.vat and not check_func(country.code.lower(), partner.vat):
                    raise ValidationError("El numero de documento [{vat}] no parece ser correcto para el tipo [{type}]".format(
                        vat=partner.vat,
                        type=partner.partner_document_type_id.name
                    ))
            else:
                super(ResPartner, partner).check_vat()
    
    @api.model
    def _commercial_fields(self):
        return super(ResPartner, self)._commercial_fields() + ['partner_document_type_id', 'country_id']
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
