# -*- encoding: utf-8 -*-

from odoo import models, fields


class AccountTax(models.Model):
    _inherit = 'account.tax'

    vat_diary_sequence = fields.Integer(
        string='Orden en subdiario',
        copy=False,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
