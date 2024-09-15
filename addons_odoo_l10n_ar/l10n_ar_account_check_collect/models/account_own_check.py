# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountOwnCheck(models.Model):
    _inherit = 'account.own.check'

    collect_move_id = fields.Many2one(
        'account.move',
        'Asiento de cobro',
        help="Asiento donde se registró el cobro de cheque",
        track_visibility='onchange',
        ondelete='restrict',
    )
    collect_check_move_id = fields.Many2one(
        'account.move',
        'Asiento del cheque',
        help="Asiento donde se registró el débito de la cuenta del cheque",
        track_visibility='onchange',
        ondelete='restrict',
    )
    collect_date = fields.Date(
        string='Fecha de cobro',
        track_visibility='onchange'
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        related=False,
        compute="_compute_company_id"
    )

    @api.depends('payment_id', 'collect_move_id')
    def _compute_company_id(self):
        for rec in self:
            rec.company_id = rec.payment_id.company_id.id or rec.collect_move_id.company_id.id

    def get_reconcile_valid_check_states(self):
        valid_states = super(AccountOwnCheck, self).get_reconcile_valid_check_states()
        valid_states.append('collect')
        return valid_states

    def get_reconcile_check_state_error(self):
        error_msg = super(AccountOwnCheck, self).get_reconcile_check_state_error()
        error_msg += " o cobrados."
        return error_msg

    def get_states(self):
        res = super(AccountOwnCheck, self).get_states()
        res.insert(3, ('collect', 'Cobrado'))
        return res
    
    def get_cancel_states(self):
        res = super(AccountOwnCheck, self).get_cancel_states()
        res.update({
            'collect': 'draft',
            'reconciled_collect': 'collect',
        })
        return res

    def get_next_states(self):
        res = super(AccountOwnCheck, self).get_next_states()
        res.update({
            'draft_collect': 'collect',
        })
        return res

    @api.constrains('payment_date', 'collect_date')
    def constraint_collect_date(self):
        for check in self:
            if check.collect_date and check.collect_date < check.payment_date:
                raise ValidationError("La fecha de cobro no puede ser menor a la fecha de pago")

    def post_collect(self, vals):
        """ Lo que deberia pasar con el cheque cuando se cobra.. """
        if any(check.state != 'draft' for check in self):
            raise ValidationError("Los cheques propios a cobrar deben estar en estado borrador")
        self.write(vals)
        self.next_state('draft_collect')

    def cancel_collect(self):
        """ Lo que deberia pasar con el cheque cuando se revierte el cobro.. """
        if any(check.state != 'collect' for check in self):
            raise ValidationError("Los cheques propios deben estar en estado cobrado para revertir el cobro")
        self.cancel_state('collect')
        collect_move_id = self.collect_move_id
        collect_check_move_id = self.collect_check_move_id
        self.write({
            'collect_move_id': False,
            'collect_check_move_id': False,
            'collect_date': False
        })
        collect_move_id.button_draft()
        collect_move_id.with_context(force_delete=True).unlink()
        collect_check_move_id.button_draft()
        collect_check_move_id.with_context(force_delete=True).unlink()

    def _cancel_reconcile_state(self):
        if self.collect_move_id:
            self.cancel_state('reconciled_collect')
        else:
            return super()._cancel_reconcile_state()
        
    def _get_own_check_view(self):
        """
        Devuelve la vista form de un cheque cobrado
        """
        return {
            'name': 'Cheque cobrado',
            'views': [[False, "form"]],
            'res_model': 'account.own.check',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
