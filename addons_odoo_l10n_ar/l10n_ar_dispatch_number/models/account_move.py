# -*- encoding: utf-8 -*-

from collections import defaultdict

from odoo import models
from odoo.tools import float_compare, float_is_zero
from odoo.tools.misc import formatLang

class AccountMove(models.Model):

    _inherit = "account.move"

    def _get_invoiced_lot_values(self):
        if not bool(self.env['ir.config_parameter'].sudo().get_param('l10n_ar_dispatch_number.use_billing_first')):
            res = super(AccountMove, self)._get_invoiced_lot_values()
            
            stock_lot_proxy = self.env['stock.lot']
            for line in res:
                lot_id = stock_lot_proxy.browse([line.get('lot_id')])
                # Tomo el ultimo número del lote
                line['dispatch_number'] = lot_id.dispatch_number.split(',')[-1].strip() if lot_id.dispatch_number else ''
                line['product_id'] = lot_id.product_id.id
        else:
            # Se pisa la logica original para los casos donde se factura primero
            # para considerar dichos casos hay que modificar la forma en la que se obtienen los remitos 

            res = []
            # if self.state == 'draft' or not self.invoice_date or self.move_type not in ('out_invoice', 'out_refund'):
            #     return res

            current_invoice_amls = self.invoice_line_ids.filtered(lambda aml: aml.display_type == 'product' and aml.product_id and aml.product_id.type in ('consu', 'product') and aml.quantity)
            all_invoices_amls = current_invoice_amls.sale_line_ids.invoice_lines.filtered(lambda aml: aml.move_id.state == 'posted').sorted(lambda aml: (aml.date, aml.move_name, aml.id))
            index = all_invoices_amls.ids.index(current_invoice_amls[:1].id) if current_invoice_amls[:1] in all_invoices_amls else 0
            previous_amls = all_invoices_amls[:index]
            invoiced_qties = current_invoice_amls._get_invoiced_qty_per_product()
            invoiced_products = invoiced_qties.keys()

            if self.move_type == 'out_invoice':
                # filter out the invoices that have been fully refund and re-invoice otherwise, the quantities would be
                # consumed by the reversed invoice and won't be print on the new draft invoice
                previous_amls = previous_amls.filtered(lambda aml: aml.move_id.payment_state != 'reversed')

            previous_qties_invoiced = previous_amls._get_invoiced_qty_per_product()

            if self.move_type == 'out_refund':
                # we swap the sign because it's a refund, and it would print negative number otherwise
                for p in previous_qties_invoiced:
                    previous_qties_invoiced[p] = -previous_qties_invoiced[p]
                for p in invoiced_qties:
                    invoiced_qties[p] = -invoiced_qties[p]

            qties_per_lot = defaultdict(float)
            previous_qties_delivered = defaultdict(float)
            # Se añade al filtro el estado assigned, para los casos donde se factura primero
            stock_move_lines = current_invoice_amls.sale_line_ids.move_ids.move_line_ids.filtered(lambda sml: sml.state in ('done', 'assigned') and sml.lot_id).sorted(lambda sml: (sml.date, sml.id))
            for sml in stock_move_lines:
                if sml.product_id not in invoiced_products or 'customer' not in {sml.location_id.usage, sml.location_dest_id.usage}:
                    continue
                product = sml.product_id
                product_uom = product.uom_id
                quantity = sml.product_uom_id._compute_quantity(sml.quantity, product_uom)

                # is it a stock return considering the document type (should it be it thought of as positively or negatively?)
                is_stock_return = (
                        self.move_type == 'out_invoice' and (sml.location_id.usage, sml.location_dest_id.usage) == ('customer', 'internal')
                        or
                        self.move_type == 'out_refund' and (sml.location_id.usage, sml.location_dest_id.usage) == ('internal', 'customer')
                )
                if is_stock_return:
                    returned_qty = min(qties_per_lot[sml.lot_id], quantity)
                    qties_per_lot[sml.lot_id] -= returned_qty
                    quantity = returned_qty - quantity

                previous_qty_invoiced = previous_qties_invoiced[product]
                previous_qty_delivered = previous_qties_delivered[product]
                # If we return more than currently delivered (i.e., quantity < 0), we remove the surplus
                # from the previously delivered (and quantity becomes zero). If it's a delivery, we first
                # try to reach the previous_qty_invoiced
                if float_compare(quantity, 0, precision_rounding=product_uom.rounding) < 0 or \
                        float_compare(previous_qty_delivered, previous_qty_invoiced, precision_rounding=product_uom.rounding) < 0:
                    previously_done = quantity if is_stock_return else min(previous_qty_invoiced - previous_qty_delivered, quantity)
                    previous_qties_delivered[product] += previously_done
                    quantity -= previously_done

                qties_per_lot[sml.lot_id] += quantity

            for lot, qty in qties_per_lot.items():
                # access the lot as a superuser in order to avoid an error
                # when a user prints an invoice without having the stock access
                lot = lot.sudo()
                if float_is_zero(invoiced_qties[lot.product_id], precision_rounding=lot.product_uom_id.rounding) \
                        or float_compare(qty, 0, precision_rounding=lot.product_uom_id.rounding) <= 0:
                    continue
                invoiced_lot_qty = min(qty, invoiced_qties[lot.product_id])
                invoiced_qties[lot.product_id] -= invoiced_lot_qty
                # Se añade numero de despacho y id del producto
                res.append({
                    'product_name': lot.product_id.display_name,
                    'quantity': formatLang(self.env, invoiced_lot_qty, dp='Product Unit of Measure'),
                    'uom_name': lot.product_uom_id.name,
                    'lot_name': lot.name,
                    'lot_id': lot.id,
                    'dispatch_number': lot.dispatch_number.split(',')[-1].strip() if lot.dispatch_number else '',  # Tomo el ultimo número del lote
                    'product_id': lot.product_id.id,
                })

        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
