# -*- encoding: utf-8 -*-

from odoo import models, fields


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    reports_name = fields.Char(
        string='Nombre en reportes',
        copy=False
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
