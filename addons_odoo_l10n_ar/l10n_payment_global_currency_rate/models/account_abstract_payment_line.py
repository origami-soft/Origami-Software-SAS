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


class AccountAbstractPaymentLine(models.AbstractModel):

    _inherit = 'account.abstract.payment.line'

    payment_currency_rate = fields.Float(related='payment_id.currency_rate')
    payment_current_currency_rate = fields.Float(related='payment_id.current_currency_rate')

    def get_rate_field(self, payment):
        """ Como ya no tomamos la cotizacion de la linea, usamos los nuevos campos """
        if self.currency_id == self.company_id.currency_id:
            return super(AccountAbstractPaymentLine, self).get_rate_field(payment)
        return 'payment_currency_rate' if self.payment_currency_rate else 'payment_current_currency_rate'

    @api.onchange('journal_id')
    def onchange_update_rate(self):
        res = super(AccountAbstractPaymentLine, self).onchange_update_rate()
        if self.currency_id == self.company_id.currency_id:
            self.rate = self.payment_currency_rate if self.payment_currency_rate else self.payment_current_currency_rate
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
