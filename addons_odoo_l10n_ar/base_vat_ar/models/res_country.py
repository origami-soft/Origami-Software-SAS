# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class ResCountry(models.Model):

    _inherit = 'res.country'

    @api.model
    def set_ar_no_prefix(self):
        self.env.ref('base.ar').no_prefix = True

    vat = fields.Char(string='Cuit de pais', help='Solo se utiliza en los casos de exportacion.')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
