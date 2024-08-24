# -*- encoding: utf-8 -*-

from odoo import models, fields


class AccountPaymentTypeLine(models.Model):
    _name = 'account.payment.type.line'
    _inherit = 'account.abstract.payment.line'
    _description = 'Línea de método de pago'

    name = fields.Char(string="Concepto")
    journal_id = fields.Many2one(
        domain="[('company_id', '=', company_id), ('type', 'in', ['cash', 'bank']), \
                 ('payment_usage', '=', 'payment_type')]"
    )
    journal_name = fields.Char(related='journal_id.name')
    date = fields.Date(string='Fecha de método')

    def get_line_error_description(self):
        return "método de pago {}".format(self.journal_name)

    def get_date_field(self):
        return 'date'

    def get_observation(self):
        return 'journal_name' if self.name else 'name'
    
    def get_move_vals(self, payment):
        res = super().get_move_vals(payment)
        res['date'] = self.date
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
