# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    full_voucher_name = fields.Char(related='move_id.full_voucher_name')

    def _get_integrity_hash_fields(self):
        res = super()._get_integrity_hash_fields()
        if self._context.get('skip_invoice_integrity_check'):
            return [x for x in res if x not in self.move_id._get_fields_to_skip()]
        return res

    @api.depends('move_id', 'ref', 'product_id', 'move_id.full_voucher_name')
    def _compute_display_name(self):
        for line in self:
            elements = set([line.move_id.full_voucher_name,
                line.ref and f"({line.ref})",
                line.name or line.product_id.display_name])
            line.display_name = " ".join(element for element in elements if element)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: