# -*- encoding: utf-8 -*-

from odoo import models, fields

product_concept_selection = [
    ('consu', 'Consumible'),
    ('service', 'Service'),
    ('product', 'Almacenable'),
]


class AfipConcept(models.Model):
    _name = 'afip.concept'
    _description = 'Concepto de Afip'

    name = fields.Char('Nombre', required=True)
    product_concept_ids = fields.Many2many(
        'product.concept.category',
        string='Categoria de conceptos'
    )


class ProductConcept(models.Model):
    _name = 'product.concept'
    _description = 'Concepto de producto'

    name = fields.Char('Descripcion', required=True)
    type = fields.Selection(
        string='Tipo',
        selection=product_concept_selection,
        required=True
    )
    product_concept_category_id = fields.Many2one(
        'product.concept.category',
        'Categoria de concepto',
        required=True
    )


class ProductConceptCategory(models.Model):
    _name = 'product.concept.category'
    _description = 'Categoría de concepto de producto'

    name = fields.Char('Nombre', required=True)
    afip_concept_ids = fields.Many2many('afip.concept', string='Concepto Afip')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
