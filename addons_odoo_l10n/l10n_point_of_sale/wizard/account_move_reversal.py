# -*- encoding: utf-8 -*-

from odoo import models, _


class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    def _prepare_default_reversal(self, move):
        res = super()._prepare_default_reversal(move)
        res['ref'] = res['ref'].replace(move.name, move.full_voucher_name)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
