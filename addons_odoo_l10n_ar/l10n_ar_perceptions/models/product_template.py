# -*- encoding: utf-8 -*-

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    perception_taxable = fields.Boolean('Aplica percepción', default=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
