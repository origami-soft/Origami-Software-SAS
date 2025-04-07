# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    unique_product_code = fields.Char('Código unico de producto')

    @api.constrains('unique_product_code')
    def check_arba_code(self):
        for rec in self.filtered('unique_product_code'):
            if len(rec.unique_product_code) != 6 or not rec.unique_product_code.isdigit():
                raise ValidationError(
                    'El código según nomenclador de ARBA debe ser de 6 dígitos'
                    ' numéricos')

    def action_arba_codes(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': 'http://www.arba.gov.ar/Aplicaciones/NomencladorTB/NomencladorTB.asp',
            'target': 'new'
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
