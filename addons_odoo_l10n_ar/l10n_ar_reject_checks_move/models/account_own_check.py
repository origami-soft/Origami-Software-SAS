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

    def get_reject_move_vals(self):
        debit_line = {}
        credit_line = {}
        message = 'Rechazo de cheque propio: {}'.format(self.name)
        if self.state == 'handed':
            # Debe: Cuenta a pagar del partner (La linea con la cuenta a pagar tiene que tener partner.)
            if not self.destination_partner_id:
                raise ValidationError("El cheque no tiene partner destino.")
            debit_line = self._get_reject_move_line(
                self.destination_partner_id.with_context(force_company=self.company_id.id).property_account_payable_id,
                credit=self.amount,
                partner_id=self.destination_partner_id.id,
                reference=message
            )
            # Haber
            credit_line = self._get_reject_move_line(
                self.journal_id.default_credit_account_id,
                debit=self.amount,
                reference=message
            )

        vals = {
            'date': fields.Date.today(),
            'ref': message,
            'journal_id': self.journal_id.id,
            'line_ids': [(0, 0, debit_line), (0, 0, credit_line)]
        }
        return vals

    def _get_reject_move_line(self, account, debit=0.0, credit=0.0, partner_id=False, reference=''):
        """
        Crea una move line de la venta de cheques y las asocia al move
        :param account: Cuenta contable de la linea del asiento
        :param debit: Importe en el haber de la move line
        :param credit: Importe en el haber de la move line
        :param partner_id: Id del partner de la linea del asiento (opcional)
        :param reference: Descripcion de la linea contable
        :return: account.move.line creada
        """
        move_line_vals = {
            'debit': debit,
            'credit': credit,
            'name': reference,
            'account_id': account.id,
            'partner_id': partner_id,
        }
        return move_line_vals

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
