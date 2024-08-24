# -*- encoding: utf-8 -*-

from odoo import models


class RegisterAccountPaymentTypeLine(models.TransientModel):
    _name = 'register.account.payment.type.line'
    _inherit = ['account.payment.type.line', 'register.account.abstract.payment.line']
    _description = 'Línea de método de pago en "Registrar pago"'

    def get_payment_line_vals(self):
        res = super().get_payment_line_vals()
        res['date'] = self.date
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
