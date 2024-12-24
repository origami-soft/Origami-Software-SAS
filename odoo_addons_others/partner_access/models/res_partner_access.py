# -*- encoding: utf-8 -*-

from odoo import models, fields


class ResPartnerAccess(models.Model):

    _name = 'res.partner.access'

    _inherit = ['mail.thread']

    name = fields.Char(
        string="Descripcion",
        required=True
    )

    application = fields.Char(
        string="Aplicacion",
        tracking=True,
    )

    user = fields.Char(
        string="Usuario",
        tracking=True,
    )

    password = fields.Char(
        string="Password",
        tracking=True,
    )

    host = fields.Char(
        string="Host",
        tracking=True,
    )

    port = fields.Char(
        string="Puerto",
        tracking=True,
    )

    file = fields.Binary(
        string="Archivo",
    )

    filename = fields.Char(
        string="Nombre de archivo",
    )

    note = fields.Text(
        string="Nota",
    )

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        required=True
    )

    active = fields.Boolean(
        string="Activo",
        default=True,
    )

    def _default_category(self):
        return self.env['res.partner.access.category'].browse(self._context.get('category_ids'))

    category_ids = fields.Many2many(
        comodel_name='res.partner.access.category',
        column1='access_id',
        column2='category_id',
        string='Categorias',
        default=_default_category
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
