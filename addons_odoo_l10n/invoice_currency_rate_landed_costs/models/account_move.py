# -*- encoding: utf-8 -*-

from odoo import models


class AccountMove(models.Model):

    _inherit = 'account.move'

    def button_create_landed_costs(self):
        if self.need_rate and self.currency_rate:
            self = self.with_context(
                fixed_rate=self.currency_rate,
                fixed_from_currency=self.currency_id,
                fixed_to_currency=self.company_id.currency_id
            )
        return super(AccountMove, self).button_create_landed_costs()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
