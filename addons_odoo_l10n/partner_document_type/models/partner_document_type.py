# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PartnerDocumentType(models.Model):
    _name = 'partner.document.type'
    _description = 'Tipo de documento de partner'

    name = fields.Char(
        string='Nombre', 
        required=True
    )
    verification_required = fields.Boolean(
        string='¿Valida documento?'
    )
    active = fields.Boolean(
        string='Activo',
        default=True,
    )
    foo = fields.Char(
        string='Funcion de validacion de documento'
    )
    address_required = fields.Boolean(
        string='Requiere direccion'
    )

    @api.constrains("verification_required", "foo")
    def check_foo(self):
        for document_type in self:
            if document_type.verification_required and not document_type.foo:
                raise ValidationError("No existe funcion asociada para validar este tipo de documento")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
