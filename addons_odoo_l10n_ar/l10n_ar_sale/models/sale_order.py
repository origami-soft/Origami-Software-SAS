# -*- encoding: utf-8 -*-

from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        res.update({
            'jurisdiction_id': (self.partner_shipping_id.state_id or self.partner_id.state_id).id,
            'name': '/'
        })
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
