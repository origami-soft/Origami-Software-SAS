# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    insurance_value = fields.Float(
        string="Valor del seguro",
        store=True,
        digits=(10,2),
    )

    def action_done(self):
        res = super().action_done()
        for r in self.filtered(lambda l: l.carrier_id and l.picking_type_code == 'outgoing' and not l.insurance_value):
            r.insurance_value = r.get_insurance_value()
        return res

    def get_insurance_value(self):
        self.ensure_one()
        value = 0
        for line in self.move_ids_without_package.filtered(lambda l: l.sale_line_id.product_uom_qty > 0):
            price_unit = line.sale_line_id.price_subtotal / line.sale_line_id.product_uom_qty
            line_value = price_unit * (self.carrier_id.coefficient_value / 100) * line.quantity_done
            value += line_value
        return value

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: