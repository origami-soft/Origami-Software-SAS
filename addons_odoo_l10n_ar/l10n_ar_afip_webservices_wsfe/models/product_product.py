# -*- encoding: utf-8 -*-

from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    ncm_id = fields.Many2one(
        comodel_name='ncm.types',
        string='NCM',
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
