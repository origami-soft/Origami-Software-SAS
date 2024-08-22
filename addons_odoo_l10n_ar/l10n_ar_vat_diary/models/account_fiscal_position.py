# -*- encoding: utf-8 -*-

from odoo import models, fields


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    show_vat_diary = fields.Boolean(
        string='Mostrar en subdiario',
        copy=False,
        default=True,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
