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

from odoo import models, fields


class AccountPaymentTypeLine(models.Model):
    _name = 'account.payment.type.line'
    _inherit = 'account.abstract.payment.line'
    _description = 'Líneas de método de pago'

    name = fields.Char(string="Concepto")
    journal_id = fields.Many2one(
        domain="[('company_id', '=', company_id), ('type', 'in', ['cash', 'bank']), \
                 ('multiple_payment_journal', '=', False), ('payment_method_of_multiple_payment', '=', True)]"
    )
    journal_name = fields.Char(related='journal_id.name')
    date = fields.Date(
        string='Fecha de método',
    )

    def get_date_field(self):
        return 'date'

    def get_observation(self):
        super(AccountPaymentTypeLine, self).get_observation()
        return 'journal_name' if self.name else 'name'
    
    def get_move_vals(self, payment):
        res = super().get_move_vals(payment)
        res['date'] = self.date
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
