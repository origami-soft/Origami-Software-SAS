# -*- encoding: utf-8 -*-

from odoo import models

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _invoice_paid_hook(self):
        """ Sobrescribo el método para poner el número correcto en el mensaje de factura pagada en la OV """
        todo = set()
        for invoice in self.filtered(lambda move: move.is_invoice()):
            for line in invoice.invoice_line_ids:
                for sale_line in line.sale_line_ids:
                    todo.add((sale_line.order_id, invoice.full_voucher_name))
        for (order, name) in todo:
            order.message_post(body=f"Factura {name} pagada")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
