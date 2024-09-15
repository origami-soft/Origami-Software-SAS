# -*- encoding: utf-8 -*-

from odoo import models, fields


class AccountCheckLocation(models.Model):
    _name = 'account.check.location'
    _description = 'Ubicaciones de cheques'

    name = fields.Char(
        string='Ubicación',
        required=True
    )
    prefix = fields.Char(
        string='Prefijo',
        help='Prefijo para agregar en el nombre del cheque'
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
