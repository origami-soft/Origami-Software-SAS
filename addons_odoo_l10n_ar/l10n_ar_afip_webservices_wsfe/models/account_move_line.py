# -*- coding: utf-8 -*-

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def get_vat_balance(self):
        return abs(self.amount_currency)

    def get_other_tributes_balance(self):
        return abs(self.amount_currency if self.amount_currency else self.balance)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
