# -*- encoding: utf-8 -*-

from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):

    _inherit = 'sale.advance.payment.inv'

    def _prepare_invoice_values(self, order, down_payment_lines):
        res = super()._prepare_invoice_values(order, down_payment_lines)
        res['jurisdiction_id'] = (order.partner_shipping_id.state_id or order.partner_id.state_id).id
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
