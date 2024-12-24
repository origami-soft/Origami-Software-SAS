# -*- encoding: utf-8 -*-

from odoo import models, fields


class ResPartnerAccessCategory(models.Model):

    _description = 'Categoria Accesos'

    _name = 'res.partner.access.category'

    name = fields.Char(
        string='Nombre',
        required=True
    )

    color = fields.Integer(
        string='Color'
    )

    active = fields.Boolean(
        string="Activo",
        default=True
    )

    access_ids = fields.Many2many(
        'res.partner.access',
        column1='category_id',
        column2='access_id',
        string='Accesos'
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
