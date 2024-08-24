# -*- encoding: utf-8 -*-

from odoo import models


class RegisterAccountThirdCheck(models.TransientModel):
    _name = 'register.account.third.check'
    _inherit = ['account.third.check', 'register.account.abstract.payment.line']
    _description = 'Cheque de terceros en "Registrar pago"'

    def get_payment_line_vals(self):
        res = super().get_payment_line_vals()
        res.update({
            'bank_id': self.bank_id.id,
            'check_type': self.check_type,
            'issue_date': self.issue_date,
            'issue_name': self.issue_name,
            'not_to_order': self.not_to_order,
            'payment_date': self.payment_date,
            'sent_rate': self.sent_rate,
        })
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
