# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class AccountPaymentRegister(models.TransientModel):

    _inherit = 'account.payment.register'

    retention_ids = fields.One2many(
        'register.account.payment.retention',
        'payment_id',
        'Retenciones'
    )

    @api.onchange('retention_ids')
    def onchange_retention_ids(self):
        self.recalculate_difference()

    def _create_payment_vals_from_wizard(self, batch_result):
        res = super()._create_payment_vals_from_wizard(batch_result)
        res['retention_ids'] = [(0, 0, r.get_payment_line_vals()) for r in self.retention_ids]
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
