# -*- coding: utf-8 -*-

from odoo import models, fields


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'
    
    get_cot_automatically = fields.Boolean(
        'Obtener COT Automaticamente', 
        help="Se intentara obtener el COT una vez se valide el remito"
    ) 

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
