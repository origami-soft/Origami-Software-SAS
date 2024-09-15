# -*- encoding: utf-8 -*-

from odoo import models


class RegisterAccountPaymentCreditCardLine(models.TransientModel):
    _name = 'register.account.payment.credit.card.line'
    _inherit = ['account.payment.credit.card.line', 'register.account.abstract.payment.line']
    _description = 'Tarjetas de credito "Registrar pago"'

    def get_payment_line_vals(self):
        res = super().get_payment_line_vals()
        res.update({
            'credit_card_id': self.credit_card_id.id,
            'payment_plan_id': self.payment_plan_id.id,
            'credit_card_name': self.credit_card_name,
            'name': self.name
        })
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
