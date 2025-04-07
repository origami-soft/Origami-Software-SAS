# -*- coding: utf-8 -*-

from odoo import models, fields


class StockLot(models.Model):
    _inherit = 'stock.lot'

    dispatch_number = fields.Char(string="Número de Despacho")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
