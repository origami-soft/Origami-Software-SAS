# -*- encoding: utf-8 -*-

from odoo import models


class AccountFiscalPosition(models.Model):

    _inherit = 'account.fiscal.position'

    # def get_available_denominations(self, receipt_fiscal_position):
    #     return self.ar_fiscal_position_id.get_denomination(receipt_fiscal_position.ar_fiscal_position_id)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
