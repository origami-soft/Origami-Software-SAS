# -*- encoding: utf-8 -*-

from ..wizard.wizard_own_check_reconcile import MOVE_LINE_LABEL
from odoo import models, fields
from odoo.exceptions import ValidationError


class AccountOwnCheck(models.Model):
    _inherit = 'account.own.check'

    reconcile_move_ids = fields.One2many(
        comodel_name='account.move',
        inverse_name='reconciled_check_id',
        string="Asientos de débito"
    )
    reconcile_date = fields.Date(string="Fecha de débito")

    def get_reconcile_vals(self):
        self.ensure_one()
        return {
            'check_id': self.id,
            'amount': self.amount,
            'check_account_id': self.journal_id._get_journal_outbound_outstanding_payment_accounts()[0].id,
            'account_id': self.bank_journal_id._get_journal_outbound_outstanding_payment_accounts()[0].id,
            'currency_id': self.currency_id.id,
            'company_id': self.company_id.id,
        }

    def get_reconcile_valid_check_states(self):
        return ['handed']

    def get_reconcile_check_state_error(self):
        return "Los cheques propios a debitar deben estar entregados"
    
    def get_states(self):
        res = super(AccountOwnCheck, self).get_states()
        res.append(('reconciled', "Debitado"))
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
        """ Lo que deberia pasar con el cheque cuando se lo debita """
        valid_states = self.get_reconcile_valid_check_states()
        if any(c.state not in valid_states for c in self):
            raise ValidationError(self.get_reconcile_check_state_error())
        self.next_state('handed_reconciled')
        vals = vals or {}
        self.write(vals)
    
    def _cancel_reconcile_state(self):
        if not self.destination_payment_id:
            raise ValidationError("No es posible cancelar el registro de débito ya que no hay información suficiente para determinar el estado anterior del cheque.")
        self.cancel_state('reconciled_handed')

    def cancel_reconcile(self):
        """ Lo que deberia pasar con el cheque cuando se cancela su registro de débito """
        if any(check.state != 'reconciled' for check in self):
            raise ValidationError("Los cheques propios deben estar debitados para cancelar el registro de débito.")
        for r in self:
            r._cancel_reconcile_state()
        self.mapped('reconcile_move_ids').button_draft()
        self.mapped('reconcile_move_ids').button_cancel()
        self.mapped('reconcile_move_ids').with_context(force_delete=True).unlink()
    
    def rename_moves(self, previous_number):
        res = super().rename_moves(previous_number)
        prev_move_line_name = MOVE_LINE_LABEL.format(previous_number)
        move_lines = self.mapped('reconcile_move_ids.line_ids').filtered(lambda l: l.name == prev_move_line_name)
        move_lines.write({'name': MOVE_LINE_LABEL.format(self.name)})
        return res
    
    def view_reconcile_moves(self):
        self.ensure_one()
        res = {
            'type': 'ir.actions.act_window',
            'views': [[False, 'form']],
            'res_model': 'account.move',
        }
        moves = self.reconcile_move_ids
        if len(moves) == 1:
            res['res_id'] = moves[0].id
        else:
            res['name'] = "Asientos de débito"
            res['views'].insert(0, [False, 'list'])
            res['domain'] = [('reconciled_check_id', '=', self.id)]
        return res

    def btn_debit(self):
        view = self.env.ref('l10n_own_check_reconcile.wizard_own_check_reconcile_form')
        model = self.env.ref('l10n_own_check_reconcile.model_account_own_check')
        return {
            'name': 'Debitar',
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.own.check.reconcile',
            'view_mode': 'form',
            'view_id': view.id,
            'binding_model_id': model.id,
            'binding_view_types':list,
            'groups_id': [(4, self.env.ref('l10n_treasury.group_account_treasury_manager').id)],
            'target': 'new',
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
