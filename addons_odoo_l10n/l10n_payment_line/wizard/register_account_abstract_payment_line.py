# -*- encoding: utf-8 -*-

from odoo import models, fields


class RegisterAccountAbstractPaymentLine(models.AbstractModel):
    _name = 'register.account.abstract.payment.line'
    _inherit = 'account.abstract.payment.line'
    _description = 'Modelo abstracto de líneas de método de pago para "Registrar pago"'

    payment_id = fields.Many2one(comodel_name='account.payment.register')
    date_abstract_payment = fields.Date(string="Fecha", related='payment_id.payment_date')

    def get_payment_line_vals(self):
        return {
            'amount': self.amount,
            'company_id': self.company_id.id,
            'journal_id': self.journal_id.id,
            'name': self.name,
            'payment_currency_amount': self.payment_currency_amount,
            'rate': self.rate,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
