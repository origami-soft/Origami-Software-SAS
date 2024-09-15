# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class AccountPaymentRegister(models.TransientModel):

    _inherit = 'account.payment.register'

    credit_card_line_ids = fields.One2many(
        'register.account.payment.credit.card.line',
        'payment_id',
        'Tarjetas de crédito'
    )

    @api.onchange('credit_card_line_ids')
    def onchange_credit_card_line_ids(self):
        self.recalculate_difference()

    def _create_payment_vals_from_wizard(self, batch_result):
        res = super()._create_payment_vals_from_wizard(batch_result)
        res['credit_card_line_ids'] = [(0, 0, r.get_payment_line_vals()) for r in self.credit_card_line_ids]
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
