# -*- coding: utf-8 -*-

from odoo import models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def action_arba_codes(self):
        return self.product_tmpl_id.action_arba_codes()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
