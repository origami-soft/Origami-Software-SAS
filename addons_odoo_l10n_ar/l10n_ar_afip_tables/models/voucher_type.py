# -*- encoding: utf-8 -*-

from odoo import models, fields


class VoucherType(models.Model):

    _inherit = 'voucher.type'

    is_credit_invoice = fields.Boolean('Factura de credito')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
