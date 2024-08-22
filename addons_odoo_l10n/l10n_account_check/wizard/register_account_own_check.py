# -*- encoding: utf-8 -*-

from odoo import models


class RegisterAccountOwnCheck(models.TransientModel):
    _name = 'register.account.own.check'
    _inherit = ['account.own.check', 'register.account.abstract.payment.line']
    _description = 'Cheque propio en "Registrar pago"'

    def get_payment_line_vals(self):
        res = super().get_payment_line_vals()
        res.update({
            'bank_id': self.bank_id.id,
            'bank_journal_id': self.bank_journal_id.id,
            'check_type': self.check_type,
            'issue_date': self.issue_date,
            'payment_date': self.payment_date,
        })
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
