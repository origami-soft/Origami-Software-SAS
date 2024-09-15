# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    payment_type_line_ids = fields.One2many('account.payment.type.line', 'payment_id', string="Líneas de métodos de pago")

    show_date_in_payment_type_line = fields.Boolean(related='company_id.show_date_in_payment_type_line')

    def unlink(self):
        """ Heredo el método unlink() ya que al eliminar un pago, 
        si no se define explícitamente eliminar las líneas también 
        Odoo intentará poner NULL en todos los campos de las líneas,
        generando errores por constraint not null """
        for payment in self:
            payment.payment_type_line_ids.unlink()
        return super(AccountPayment, self).unlink()

    @api.onchange('payment_type_line_ids')
    def onchange_payment_type_line_ids(self):
        self.recalculate_payment_amount()

    def get_payment_line_fields(self):
        res = super(AccountPayment, self).get_payment_line_fields()
        res.append('payment_type_line_ids')
        return res

    def action_post(self):
        for rec in self:
            rec.payment_type_line_ids.filtered(lambda x: not x.date).write({'date': rec.date})
        return super(AccountPayment, self).action_post()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
