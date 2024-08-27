# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class AccountPaymentCreditCardLine(models.Model):

    _name = 'account.payment.credit.card.line'
    _inherit = 'account.abstract.payment.line'
    _description = 'Línea de tarjeta de crédito en pagos'

    credit_card_id = fields.Many2one(
        'credit.card',
        "Tarjeta",
        required=True
    )
    payment_plan_id = fields.Many2one(
        'credit.card.payment.plan',
        "Plan de pago",
        required=True,
        domain="[('credit_card_id', '=', credit_card_id)]"
    )
    name = fields.Char(required=True)
    credit_card_name = fields.Char(
        string='Nombre de la tarjeta',
        related='credit_card_id.name'
    )
    journal_id = fields.Many2one(
        domain="[('company_id', '=', company_id), ('type', 'in', ['cash', 'bank']), \
                     ('payment_usage', '=', 'credit_card')]"
    )

    @api.onchange('credit_card_id')
    def onchange_credit_card_id(self):
        self.update({
            'journal_id': self.credit_card_id.journal_id.id,
            'payment_plan_id': False
        })

    def get_observation(self):
        super(AccountPaymentCreditCardLine, self).get_observation()
        return 'credit_card_name'

    def get_first_move_line_name(self):
        return 'CUPÓN N° {}'.format(super(AccountPaymentCreditCardLine, self).get_first_move_line_name())

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
