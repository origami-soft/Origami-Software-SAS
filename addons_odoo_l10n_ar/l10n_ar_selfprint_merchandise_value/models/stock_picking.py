# -*- encoding: utf-8 -*-

from odoo import models, fields


class DeliveryCarrier(models.Model):
    _inherit = 'stock.picking'

    insurance_value = fields.Float(
        string="Valor del seguro",
        digits=(10,2),
    )

    def _action_done(self):
        res = super()._action_done()
        for r in self.filtered(lambda l: l.sale_id):
            r.insurance_value = r.get_insurance_value()
        return res

    def get_insurance_value(self):
        self.ensure_one()
        value = 0
        for line in self.move_ids_without_package.filtered(lambda l: l.sale_line_id.product_uom_qty > 0):
            price_unit = line.sale_line_id.price_subtotal / line.sale_line_id.product_uom_qty
            line_value = price_unit * (self.carrier_id.coefficient_value / 100) * line.quantity
            value += line_value
        return value

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
