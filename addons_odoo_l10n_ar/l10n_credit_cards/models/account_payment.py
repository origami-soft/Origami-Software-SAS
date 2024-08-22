# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class AccountPayment(models.Model):

    _inherit = 'account.payment'

    credit_card_line_ids = fields.One2many(
        'account.payment.credit.card.line',
        'payment_id',
        'Tarjetas de crédito'
    )

    def unlink(self):
        """ Heredo el método unlink() ya que al eliminar un pago, 
        si no se define explícitamente eliminar las líneas también 
        Odoo intentará poner NULL en todos los campos de las líneas,
        generando errores por constraint not null """
        for payment in self:
            payment.credit_card_line_ids.unlink()
        return super(AccountPayment, self).unlink()

    @api.onchange('credit_card_line_ids')
    def onchange_credit_card_line_ids(self):
        self.recalculate_payment_amount()

    def get_payment_line_fields(self):
        res = super(AccountPayment, self).get_payment_line_fields()
        res.extend(['credit_card_line_ids'])
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
