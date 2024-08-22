# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class ResCountry(models.Model):
    _inherit = 'res.country'
    
    no_prefix = fields.Boolean(
        string='Evitar Prefijo', 
        help=(
            "Tildar esta opción si para verificar si el documento de un partner "
            "asociado a este pais no se debe poner el prefijo del pais"
        )
    )
    not_validate_vat = fields.Boolean(
        string='No validar documento', 
        help=(
            "Tildar esta opción si para un partner asociado a este pais no se debe validar el documento"
        )
    )

    @api.model
    def set_noupdate_false(self):
        self.env.get('ir.model.data').search([('model', '=', 'res.country')]).write({'noupdate': False})
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
