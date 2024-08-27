# -*- encoding: utf-8 -*-

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _compute_all_tax(self):
        for m in self.mapped('move_id'):
            super(AccountMoveLine, self.filtered(lambda l: l.move_id == m).with_context(perception_ctx=m.get_perception_ctx()))._compute_all_tax()

    def perception_applies(self):
        self.ensure_one()
        return self.product_id and self.product_id.perception_taxable or not (self.product_id or self.display_type in ('line_section', 'line_note'))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
