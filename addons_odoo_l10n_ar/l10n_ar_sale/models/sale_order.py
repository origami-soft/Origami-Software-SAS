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


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    def _create_invoices(self, grouped=False, final=False):
        invoices = super(SaleOrder, self)._create_invoices(grouped=grouped, final=final)
        for order in self:
            order_invoices = order.invoice_ids.filtered(lambda x: x.id in invoices.ids)
            order_invoices.update({'jurisdiction_id': order.partner_shipping_id.state_id or order.partner_id.state_id})
        for invoice in invoices:
            invoice._onchange_partner_id()
            # En _onchange_partner_id se resetean las notas de la factura según
            # los términos y condiciones de la configuración general de facturación.
            # Pero el caso de uso de tal función es si el usuario manualmente cambiara
            # el cliente por lo que volvemos a setear las notas con la nota de la venta
            sale_order = invoice.line_ids.sale_line_ids.order_id
            # Solo se tiene en cuenta aquellas facturas que se hacen sobre una sola venta
            # Ya que de forma estándar cuando se agrupan facturas no tiene en cuenta la nota
            # como un dato a actualizar
            if len(sale_order) == 1:
                invoice.update({
                    'narration': sale_order.note,
                    'partner_shipping_id': sale_order.partner_shipping_id.id,
                    'invoice_payment_term_id': sale_order.payment_term_id.id,
                })
                # Llamo al onchange que recomputa así se modifica la fecha de vencimiento para que se corresponda con
                # el plazo de pago establecido
                invoice._onchange_recompute_dynamic_lines()
        return invoices

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
