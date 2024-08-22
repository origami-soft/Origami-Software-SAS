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

from odoo import models
from odoo.exceptions import ValidationError


class AccountThirdCheck(models.Model):
    _inherit = 'account.third.check'

    def button_reject_check(self):
        """
        Se rechaza el cheque si está en los estados correspondientes para ser rechazado
        :raise ValidationError: No está en alguno de los estados para ser rechazado
        """
        self.reject_check()

        # TODO: Agregar funcionalidad de creación de nota de debito (arrastrado desde V12)

    def button_revert_reject(self):
        """
        Revierte el rechazo de un cheque
        :raise ValidationError: El estado del cheque no es rechazado
        """
        self.revert_reject()

    def reject_check(self):
        """ Lo que debería pasar con el cheque cuando se rechaza"""
        if any(check.state == 'draft' for check in self):
            raise ValidationError("No se puede rechazar un cheque en borrador.")
        for check in self:
            # Se puede pasar a rechazado desde cartera, entregado, depositado o vendido
            check.next_state(check.state if check.state != 'wallet' else 'wallet_rejected')

    def revert_reject(self):
        """ Lo que deberia pasar con el cheque cuando se revierte un rechazo """
        if any(check.state != 'rejected' for check in self):
            raise ValidationError("No se puede revertir el rechazo de un cheque que no está rechazado.")

        for check in self:
            # Si antes de rechazarse estaba depositado
            if check.deposit_slip_id:
                check.cancel_state('rejected_deposited')

            # Si antes de rechazarse se lo dimos a un proveedor
            elif check.destination_payment_id and check.destination_payment_id.state != 'draft':
                check.cancel_state('rejected_handed')

            # Si no estaba depositado o entregado, debería volver a cartera
            else:
                check.cancel_state('rejected_wallet')

    def get_cancel_states(self):
        res = super(AccountThirdCheck, self).get_cancel_states()
        res['rejected_wallet'] = 'wallet'
        res['rejected_handed'] = 'handed'
        res['rejected_deposited'] = 'deposited'
        return res

    def get_next_states(self):
        res = super(AccountThirdCheck, self).get_next_states()
        res['wallet_rejected'] = 'rejected'
        res['handed'] = 'rejected'
        res['deposited'] = 'rejected'
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
