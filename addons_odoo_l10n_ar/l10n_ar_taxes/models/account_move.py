# -*- encoding: utf-8 -*-

import json
from odoo import models, fields, api


class AccountMove(models.Model):

    _inherit = 'account.move'

    """
    Comentario general: Los campos de importes de las facturas tienen el campo replicado con "signed"
    esto significa que muestra los campos en el signo que corresponda (si es nc en negativo, si no positivo).
    Considero que no es necesario hacerlo para estos campos ya que no se suelen utilizar de esa manera.
    """
    # Neto gravado
    amount_to_tax = fields.Monetary(string='Neto gravado', store=True, readonly=True, compute='_compute_amount')
    # No gravado
    amount_not_taxable = fields.Monetary(string='No gravado', store=True, readonly=True, compute='_compute_amount')
    # Exento
    amount_exempt = fields.Monetary(string='Exento', store=True, readonly=True, compute='_compute_amount')
    amounts_widget = fields.Binary(compute='_get_amount_info_JSON')

    @api.depends('amount_to_tax', 'amount_not_taxable', 'amount_exempt')
    def _get_amount_info_JSON(self):
        for inv in self:
            info = {
                'title': 'Informacion de importes',
                'outstanding': False,
                'content': [{
                    'amount_to_tax': inv.amount_to_tax,
                    'amount_not_taxable': inv.amount_not_taxable,
                    'amount_exempt': inv.amount_exempt,
                    'currency_id': inv.currency_id.id,
                }]
            }
            inv.amounts_widget = info

    def _compute_amount(self):
        res = super(AccountMove, self)._compute_amount()
        invoices = self.filtered(lambda x: x.is_invoice())
        for invoice in invoices:
            amount_exempt = sum(line.price_subtotal for line in invoice.invoice_line_ids.filtered(
                lambda x: any(tax.is_vat and tax.is_exempt for tax in x.tax_ids)
            ))
            amount_to_tax = sum(line.price_subtotal for line in invoice.invoice_line_ids.filtered(
                lambda x: any(tax.is_vat and not tax.is_exempt for tax in x.tax_ids))
            )
            # Dejamos como no gravado lo que no esta en el neto gravado ni en el importe exento
            invoice.amount_not_taxable = invoice.amount_untaxed - amount_exempt - amount_to_tax
            invoice.amount_to_tax = amount_to_tax
            invoice.amount_exempt = amount_exempt

        (self - invoices).update({
            'amount_not_taxable': None,
            'amount_to_tax': None,
            'amount_exempt': None,
        })
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
