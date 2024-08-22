# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):

    _inherit = 'sale.advance.payment.inv'

    def _create_invoice(self, order, so_line, amount):
        invoice = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        invoice.jurisdiction_id = order.partner_shipping_id.state_id or order.partner_id.state_id
        invoice._onchange_partner_id()
        invoice.update({
            'partner_shipping_id': order.partner_shipping_id.id,
            'invoice_payment_term_id': order.payment_term_id.id,
        })
        # Llamo al onchange que recomputa así se modifica la fecha de vencimiento para que se corresponda con el plazo
        # de pago establecido
        invoice._onchange_recompute_dynamic_lines()
        return invoice

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
