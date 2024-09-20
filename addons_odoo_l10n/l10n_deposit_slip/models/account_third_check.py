# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

MOVE_LINE_LABEL = "Depósito de cheque Nº {}"


class AccountThirdCheck(models.Model):
    _inherit = 'account.third.check'

    @api.depends('deposit_slip_ids')
    def get_deposit_slip_id(self):
        for check in self:
            check.deposit_slip_id = check.deposit_slip_ids[0] if check.deposit_slip_ids else None

    deposit_slip_ids = fields.Many2many(
        'account.deposit.slip',
        'third_check_deposit_slip_rel',
        'third_check_id',
        'deposit_slip_id',
        string='Boletas de deposito'
    )
    deposit_slip_id = fields.Many2one(
        'account.deposit.slip',
        'Boleta de depósito',
        compute='get_deposit_slip_id',
        store=True,
    )
    deposit_bank_id = fields.Many2one(
        'account.journal',
        'Cuenta de depósito',
        related='deposit_slip_id.journal_id',
        readonly=True
    )
    deposit_date = fields.Date(
        'Fecha de depósito',
        related='deposit_slip_id.date',
        readonly=True
    )

    @api.constrains('deposit_slip_ids')
    def deposit_slip_constraints(self):
        if any(check.state != 'wallet' for check in self):
            raise ValidationError('Solo se puede modificar la boleta de depósito de un cheque en cartera.')
        for check in self:
            if len(check.deposit_slip_ids) > 1:
                raise ValidationError("El cheque {} ya se encuentra en una boleta de depósito.".format(check.name))

    def post_deposit_slip(self):
        if any(check.state != 'wallet' for check in self):
            raise ValidationError("Todos los cheques a depositar deben estar en cartera.")
        if len(self.mapped('currency_id')) > 1:
            raise ValidationError("No se pueden depositar cheques de distintas monedas en la misma boleta de depósito.")
        self.next_state('wallet_deposited')

    def cancel_deposit_slip(self):
        if any(check.state not in ('deposited', 'wallet') for check in self):
            raise ValidationError("Para cancelar la boleta de depósito, los cheques deben estar depositados o en cartera.")
        self.cancel_state('deposited')

    def get_cancel_states(self):
        res = super(AccountThirdCheck, self).get_cancel_states()
        res['deposited'] = 'wallet'
        return res

    def get_next_states(self):
        res = super(AccountThirdCheck, self).get_next_states()
        res['wallet_deposited'] = 'deposited'
        return res
    
    def get_move_line_label_with_number(self):
        self.ensure_one()
        return MOVE_LINE_LABEL.format(self.name)
    
    def rename_moves(self, previous_number):
        res = super().rename_moves(previous_number)
        prev_move_line_name = MOVE_LINE_LABEL.format(previous_number)
        move_lines = self.deposit_slip_id.move_ids.line_ids.filtered(lambda l: l.name == prev_move_line_name)
        move_lines.write({'name': self.get_move_line_label_with_number()})
        return res

    def btn_deposit_checks(self):
        view = self.env.ref('l10n_deposit_slip.account_deposit_slip_wizard_form')
        model = self.env.ref('l10n_deposit_slip.model_account_third_check')
        return {
            'name': 'Depositar cheques',
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.deposit.slip',
            'view_mode': 'form',
            'view_id': view.id,
            'binding_model_id': model.id,
            'binding_view_types':('list','form'),
            'groups_id': [(4, self.env.ref('l10n_treasury.group_account_treasury_manager').id)],
            'target': 'new',
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
