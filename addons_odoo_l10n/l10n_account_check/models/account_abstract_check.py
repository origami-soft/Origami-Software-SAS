# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from ..exceptions import exceptions


class AccountAbstractCheck(models.AbstractModel):
    _name = 'account.abstract.check'
    _inherit = ['account.abstract.payment.line', 'mail.thread', 'mail.activity.mixin']
    _description = 'Cheque abstracto'

    name = fields.Char(
        'Número',
        required=True,
        tracking=True
    )
    bank_id = fields.Many2one(
        'res.bank',
        'Banco',
        required=True,
        tracking=True
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
        tracking=True
    )
    issue_date = fields.Date(
        'Fecha de emisión',
        required=True,
        tracking=True,
    )
    payment_date = fields.Date(
        'Fecha de pago',
        required=True,
        tracking=True,
    )
    state = fields.Selection(
        'get_states',
        string='Estado',
        required=True,
        default='draft',
        tracking=True,
        readonly=True
    )
    
    def get_states(self):
        return [
            ('draft', 'Borrador'),
            ('handed', 'Entregado'),
        ]

    def get_date_field(self):
        return 'payment_date'

    def get_observation(self):
        return 'bank_name'
    
    def get_line_error_description(self):
        return "cheque N° {}".format(self.name)

    def _check_name(self):
        return self.name.isdigit()

    @api.constrains('name')
    def constraint_name(self):
        if any(not r._check_name() for r in self):
            exceptions.non_numeric_check()

    def _check_payment_issue_date(self):
        """
        Se valida que, en caso de que las fechas de emisión y pago están cargadas, que la de pago sea igual o posterior
        a la de emisión (si al menos una de las dos no está cargada no se valida nada)
        """
        return not (self.payment_date and self.issue_date) or self.payment_date >= self.issue_date

    def _check_payment_issue_date_in_common_check(self):
        """
        Se valida que, en caso de que el cheque sea común, la fecha de pago sea igual a la de emisión (si no es común
        no se valida nada)
        """
        return self.check_type != 'common' or self.payment_date == self.issue_date

    @api.constrains('payment_date', 'issue_date', 'check_type')
    def constraint_dates(self):
        for r in self:
            if not r._check_payment_issue_date():
                exceptions.invalid_check_dates() 
            if not r._check_payment_issue_date_in_common_check():
                exceptions.non_equal_check_dates()

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
            exceptions.invalid_check_cancel_state()
        self.update({'state': cancel_state})

    def next_state(self, state):
        """ Avanza al siguiente estado del flow del cheque si corresponde """
        if not self:
            return
        next_state = self.get_next_states().get(state)
        if not next_state:
            exceptions.invalid_check_next_state()
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
        move_lines = self.payment_id.move_ids.line_ids.filtered(lambda l: l.name == prev_move_line_name)
        move_lines.write({'name': new_move_line_name})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
