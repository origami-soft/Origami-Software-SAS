# -*- encoding: utf-8 -*-

from odoo import models, api


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    @api.depends('currency_id', 'company_id', 'move_id.date', 'move_id.currency_rate')
    def _compute_currency_rate(self):
        for line in self:
            if line.move_id.currency_rate:
                line = line.with_context(
                    fixed_rate=line.move_id.currency_rate,
                    fixed_from_currency=line.move_id.currency_id,
                    fixed_to_currency=line.move_id.company_id.currency_id
                )
            super(AccountMoveLine, line)._compute_currency_rate()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
