# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    payment_type_line_ids = fields.One2many(
        comodel_name='register.account.payment.type.line',
        inverse_name='payment_id',
        string="Líneas de métodos de pago"
    )
    show_date_in_payment_type_line = fields.Boolean(
        related='company_id.show_date_in_payment_type_line'
    )

    def _create_payment_vals_from_wizard(self, batch_result):
        res = super()._create_payment_vals_from_wizard(batch_result)
        res['payment_type_line_ids'] = [(0, 0, r.get_payment_line_vals()) for r in self.payment_type_line_ids]
        return res
    
    @api.onchange('payment_type_line_ids')
    def onchange_payment_type_line_ids(self):
        self.recalculate_difference()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
