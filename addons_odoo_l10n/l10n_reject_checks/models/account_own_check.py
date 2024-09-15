# -*- encoding: utf-8 -*-

from odoo import models
from odoo.exceptions import ValidationError


class AccountOwnCheck(models.Model):
    _inherit = 'account.own.check'

    def cancel_check(self):
        """ Lo que deberia pasar con el cheque cuando se cancela """
        if any(check.state != 'draft' for check in self):
            raise ValidationError("No se puede cancelar un cheque que no está en borrador.")
        self.next_state('draft_canceled')

    def revert_canceled_check(self):
        """ Lo que deberia pasar con el cheque cuando se revierte una cancelacion """
        if any(check.state != 'canceled' for check in self):
            raise ValidationError("No se puede revertir la cancelación de un cheque que no está cancelado.")
        self.cancel_state('canceled')

    def reject_check(self):
        """ Lo que deberia pasar con el cheque cuando se rechaza """
        if any(check.state not in ('handed', 'reconciled') for check in self):
            raise ValidationError("No se puede rechazar un cheque que no está entregado.")
        for check in self:    
            check.next_state(f'{check.state}_rejected')

    def revert_reject(self):
        """ Lo que deberia pasar con el cheque cuando se revierte un rechazo """
        if any(check.state != 'rejected' for check in self):
            raise ValidationError("No se puede revertir el rechazo de un cheque que no está rechazado.")
        for check in self:
            self.cancel_state('rejected_reconciled' if check.reconcile_move_ids else 'rejected_handed')

    def get_cancel_states(self):
        res = super(AccountOwnCheck, self).get_cancel_states()
        res['canceled'] = 'draft'
        res['rejected_reconciled'] = 'reconciled'
        res['rejected_handed'] = 'handed'
        return res

    def get_next_states(self):
        res = super(AccountOwnCheck, self).get_next_states()
        res['draft_canceled'] = 'canceled'
        res['handed_rejected'] = 'rejected'
        res['reconciled_rejected'] = 'rejected'
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
