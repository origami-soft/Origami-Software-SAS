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
from ..exceptions.exceptions import NonNumericCheckError, InvalidCheckAmountError, InvalidCheckDatesError,\
    NotEqualCheckDatesError, InvalidCheckCancelStateError, InvalidCheckNextStateError


class AccountAbstractCheck(models.AbstractModel):
    _name = 'account.abstract.check'
    _inherit = ['account.abstract.payment.line', 'mail.thread', 'mail.activity.mixin']
    _description = 'Cheque abstracto'

    name = fields.Char(
        'Número',
        required=True,
        track_visibility='onchange'
    )
    bank_id = fields.Many2one(
        'res.bank',
        'Banco',
        required=True,
        track_visibility='onchange'
    )
    bank_name = fields.Char(
        related='bank_id.name'
    )
    check_type = fields.Selection(
        [('common', 'Común'),
         ('postdated', 'Diferido')],
        string="Tipo",
        required=True,
        default='postdated',
        track_visibility='onchange'
    )
    issue_date = fields.Date(
        'Fecha de emisión',
        required=True,
        track_visibility='onchange',
    )
    payment_date = fields.Date(
        'Fecha de pago',
        required=True,
        track_visibility='onchange',
    )
    state = fields.Selection(
        'get_states',
        string='Estado',
        required=True,
        default='draft',
        track_visibility='onchange',
        readonly=True
    )
    journal_id = fields.Many2one(
        domain="[('company_id', '=', company_id), ('multiple_payment_journal', '=', False), ('check_journal', '=', True)]"
    )
    def get_states(self):
        return [
            ('draft', 'Borrador'),
            ('handed', 'Entregado'),
            ('rejected', 'Rechazado'),
        ]

    def get_date_field(self):
        super(AccountAbstractCheck, self).get_date_field()
        return 'payment_date'

    def get_observation(self):
        super(AccountAbstractCheck, self).get_observation()
        return 'bank_name'

    def _check_name(self):
        return self.name.isdigit()

    @api.constrains('name')
    def constraint_name(self):
        if any(not r._check_name() for r in self):
            raise NonNumericCheckError("El número del cheque solamente puede contener números.")

    def _check_payment_issue_date(self):
        return not (self.payment_date and self.issue_date) or self.payment_date >= self.issue_date

    def _check_payment_issue_date_in_common_check(self):
        return self.check_type != 'common' or self.payment_date == self.issue_date

    @api.constrains('payment_date', 'issue_date', 'check_type')
    def constraint_dates(self):
        for r in self:
            if not r._check_payment_issue_date():
                raise InvalidCheckDatesError("La fecha de pago no puede ser anterior a la fecha de emisión.")
            if not r._check_payment_issue_date_in_common_check():
                raise NotEqualCheckDatesError("Las fechas de pago y emisión de un cheque común deben ser iguales.")

    @api.onchange('check_type', 'issue_date')
    def onchange_payment_type(self):
        if self.check_type == 'common' and self.issue_date:
            self.payment_date = self.issue_date

    def _check_state_for_cancel_payment(self):
        return self.state == 'handed'

    def get_cancel_states(self):
        raise NotImplementedError

    def get_next_states(self):
        raise NotImplementedError

    def cancel_state(self, state):
        """ Vuelve a un estado anterior del flow del cheque si corresponde """
        if not self:
            return
        cancel_state = self.get_cancel_states().get(state)
        if not cancel_state:
            raise InvalidCheckCancelStateError("No se puede cancelar el cheque en el estado actual.")
        self.update({'state': cancel_state})

    def next_state(self, state):
        """ Avanza al siguiente estado del flow del cheque si corresponde """
        if not self:
            return
        next_state = self.get_next_states().get(state)
        if not next_state:
            raise InvalidCheckNextStateError("No se puede avanzar el cheque en el estado actual.")
        self.update({'state': next_state})


    def open_correct_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'views': [[False, 'form']],
            'res_model': 'check.correct.wizard',
            'target': 'new',
        } 

    def rename_moves(self, previous_number):
        new_move_line_name = self.get_first_move_line_name()
        move_line_name_array = new_move_line_name.split(' ')
        move_line_name_array[-1] = previous_number
        prev_move_line_name = ' '.join(move_line_name_array)
        move_lines = self.payment_id.line_move_ids.filtered(lambda l: l.name == prev_move_line_name)
        move_lines.write({'name': new_move_line_name})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
