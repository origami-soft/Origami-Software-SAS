# -*- encoding: utf-8 -*-

from odoo import models, fields


class AccountDenomination(models.Model):
    _name = 'account.denomination'
    _description = 'Denominación'

    name = fields.Char(
        string='Nombre', 
        required=True
    )
    description = fields.Char(string='Descripción')

    _sql_constraints = [('name_unique', 'unique(name)', 'El nombre debe ser único por denominación')]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
