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
from odoo.exceptions import ValidationError


class AccountOwnCheck(models.Model):
    _inherit = 'account.own.check'

    reconcile_id = fields.Many2one(
        comodel_name='own.check.reconcile',
        string="Conciliación",
    )

    def get_reconcile_valid_check_states(self):
        return ['handed']

    def get_reconcile_check_state_error(self):
        return "Los cheques propios a conciliar deben estar entregados"
    
    def get_states(self):
        res = super(AccountOwnCheck, self).get_states()
        res.append(('reconciled', "Conciliado"))
        return res

    def get_cancel_states(self):
        res = super(AccountOwnCheck, self).get_cancel_states()
        res['reconciled_handed'] = 'handed'
        return res

    def get_next_states(self):
        res = super(AccountOwnCheck, self).get_next_states()
        res['handed_reconciled'] = 'reconciled'
        return res

    def reconcile_check(self, vals):
        """ Lo que deberia pasar con el cheque cuando se lo concilia """
        valid_states = self.get_reconcile_valid_check_states()
        if any(c.state not in valid_states for c in self):
            raise ValidationError(self.get_reconcile_check_state_error())
        self.next_state('handed_reconciled')
        vals = vals or {}
        self.write(vals)
    
    def _cancel_reconcile_state(self):
        if self.destination_payment_id:
            self.cancel_state('reconciled_handed')
        else:
            raise ValidationError("No es posible cancelar la conciliación ya que no hay información suficiente para determinar el estado anterior del cheque.")

    def cancel_reconcile(self):
        """ Lo que deberia pasar con el cheque cuando se cancela su conciliación """
        if any(check.state != 'reconciled' for check in self):
            raise ValidationError("Los cheques propios deben estar conciliados para cancelar la conciliación.")
        for r in self:
            r._cancel_reconcile_state()
        self.write({'reconcile_id': None})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
