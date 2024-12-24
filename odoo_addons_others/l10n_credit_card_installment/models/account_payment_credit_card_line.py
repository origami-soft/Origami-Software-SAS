# -*- encoding: utf-8 -*-

from odoo import models


class AccountPaymentCreditCardLine(models.Model):
    _inherit = 'account.payment.credit.card.line'

    def create_installments(self):
        for r in self:
            self.env['credit.card.installment'].generate_from_payment(r)

    def _get_installment_vals(self, installment, amount, due_date):
        self.ensure_one()
        vals = {
            'name': self.name,
            'credit_card_line_id': self.id,
            'total_installments': self.payment_plan_id.quantity,
            'installment': installment,
            'due_date': due_date,
            'amount': amount
        }
        return vals

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
