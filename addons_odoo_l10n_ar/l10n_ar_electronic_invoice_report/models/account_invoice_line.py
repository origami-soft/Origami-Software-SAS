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