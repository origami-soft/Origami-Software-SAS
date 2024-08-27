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

    payment_type_line_ids = fields.One2many('account.payment.type.line', 'payment_id', string="Líneas de métodos de pago")

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

    @api.onchange('payment_type', 'journal_id')
    def onchange_payment_type_clear_lines(self):
        if not self.show_payment_lines:
            self.payment_type_line_ids = False
    
    def post(self):
        for rec in self:
            rec.payment_type_line_ids.filtered(lambda x: not x.date).write({'date': rec.payment_date})
        return super(AccountPayment, self).post()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
