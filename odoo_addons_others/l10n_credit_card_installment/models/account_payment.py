# -*- encoding: utf-8 -*-

from odoo import models, fields


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    credit_card_installment_ids = fields.One2many(
        comodel_name='credit.card.installment',
        inverse_name='payment_id',
        string="Cuotas"
    )

    def action_post(self):
        self.filtered(lambda l: l.partner_type == 'supplier').mapped('credit_card_line_ids').create_installments()
        return super(AccountPayment, self).action_post()

    def action_draft(self):
        res = super(AccountPayment, self).action_draft()
        self.mapped('credit_card_installment_ids').unlink()
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
