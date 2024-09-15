# -*- encoding: utf-8 -*-

from odoo import models, fields
from odoo.tools.misc import formatLang

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    electronic_invoice_price_unit = fields.Char(compute='get_electronic_invoice_price_unit')

    def get_electronic_invoice_price_unit(self):
        for r in self:
            curr = r.currency_id or r.company_id.currency_id
            # Calculo la data de impuestos para todo lo que es IVA (usando el precio unitario como base)
            tax_data = r.tax_ids.filtered(lambda l: l.is_vat).compute_all(r.price_unit, curr, 1, r.product_id, r.move_id.partner_id)
            # Si estoy en una factura con IVA discriminado, tomo el precio unitario sin impuestos. Caso contrario, lo
            # tomo con impuestos
            total_key = 'total_excluded' if r.move_id.voucher_type_id.denomination_id.vat_discriminated else 'total_included'
            price_to_use = tax_data[total_key]
            r.electronic_invoice_price_unit = formatLang(r.env, price_to_use, dp='Product Price', currency_obj=curr)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
