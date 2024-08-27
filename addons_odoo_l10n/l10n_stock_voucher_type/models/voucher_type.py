# -*- encoding: utf-8 -*-

from odoo import models, fields


class VoucherType(models.Model):

    _inherit = 'voucher.type'

    category = fields.Selection(
        selection_add=[
            ('picking', 'Remito')
        ],
        ondelete={'picking': 'cascade'}
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
