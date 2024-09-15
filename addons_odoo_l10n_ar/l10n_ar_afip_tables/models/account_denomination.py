# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class AccountDenomination(models.Model):

    _inherit = 'account.denomination'
    _description = 'Denominación'

    validate_supplier = fields.Boolean(
        'Validar numeracion?',
        help="Valida numeracion con el formato 'xxxx-xxxxxxxx' para los documentos de proveedores"
    )
    vat_discriminated = fields.Boolean(
        string='Discrimina IVA?',
        help='Discriminacion de IVA en reporte'
    )

    active = fields.Boolean(string='Activo', default=True)

    @api.model
    def unlink(self):
        for record in self:
            record.active = False
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
