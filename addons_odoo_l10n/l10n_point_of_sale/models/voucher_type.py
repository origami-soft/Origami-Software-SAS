# -*- encoding: utf-8 -*-

from odoo import models, fields


class VoucherType(models.Model):
    _inherit = 'voucher.type'

    denomination_id = fields.Many2one(
        comodel_name='account.denomination', 
        string='Denominación'
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
