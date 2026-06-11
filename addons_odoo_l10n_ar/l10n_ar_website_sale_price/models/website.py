# -*- encoding: utf-8 -*-

from odoo import models, fields


class Website(models.Model):
    _inherit = 'website'

    show_price_wo_tax = fields.Boolean(string="Mostrar precio sin impuestos")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
