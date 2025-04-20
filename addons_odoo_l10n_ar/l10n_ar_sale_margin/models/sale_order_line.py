# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    purchase_price = fields.Float(compute=False, precompute=False)

    @api.onchange('product_id', 'company_id', 'currency_id', 'product_uom')
    def onchange_set_purchase_price(self):
        self._compute_purchase_price()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
