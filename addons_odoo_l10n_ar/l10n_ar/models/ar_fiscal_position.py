# -*- encoding: utf-8 -*-

from odoo import models, fields


class ArFiscalPosition(models.Model):
    _name = 'ar.fiscal.position'
    _description = 'Posición fiscal (AR)'

    name = fields.Char('Nombre', required=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
