# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

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
