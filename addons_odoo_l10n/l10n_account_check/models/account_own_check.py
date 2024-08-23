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
from ..exceptions.exceptions import PostPaymentNonDraftCheckError, CancelPaymentNonHandedCheckError


class AccountOwnCheck(models.Model):
    _inherit = 'account.abstract.check'
    _name = 'account.own.check'
    _description = 'Cheque propio'

    destination_payment_id = fields.Many2one(
        'account.payment',
        "Pago origen",
        help="Pago donde se utilizó el cheque",
        track_visibility='onchange'
    )
    destination_partner_id = fields.Many2one(
        related='destination_payment_id.partner_id',
        store=True
    )

    def get_states(self):
        res = super(AccountOwnCheck, self).get_states()
        res.insert(2, ('canceled', 'Anulado'))
        return res

    def _check_post_payment_state(self):
        return self.state == 'draft'

    def post_payment(self, vals):
        """ Lo que deberia pasar con el cheque cuando se valida el pago """
        if any(not r._check_post_payment_state() for r in self):
            raise PostPaymentNonDraftCheckError("Los cheques propios a utilizar deben estar en borrador.")
        self.update(vals or {})
        self.next_state('draft_handed')

    def cancel_payment(self):
        """ Lo que deberia pasar con el cheque cuando se cancela una orden de pago """
        if any(not r._check_state_for_cancel_payment() for r in self):
            raise CancelPaymentNonHandedCheckError("Los cheques deben estar entregados para cancelar el pago.")
        self.update({'destination_payment_id': None})
        self.cancel_state('handed')

    def get_cancel_states(self):
        return {
            'handed': 'draft',
        }

    def get_next_states(self):
        return {
            'draft_handed': 'handed',
        }

    def get_first_move_line_name(self):
        return 'CHEQUE PROPIO N° {}'.format(super(AccountOwnCheck, self).get_first_move_line_name())


    def open_correct_wizard(self):
        res = super().open_correct_wizard()
        res['context'] = {'default_own_check_id': self.id}
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
