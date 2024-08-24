# -*- encoding: utf-8 -*-

from odoo import models, fields


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    reports_name = fields.Char(
        string='Nombre en reportes',
        copy=False
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
