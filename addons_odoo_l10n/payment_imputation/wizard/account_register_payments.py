# -*- encoding: utf-8 -*-

from odoo import models


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def _get_imputation_vals(self, orig_lines):
        res = {}
        lines = self.env['account.move.line']
        for line in orig_lines:
            lines |= line.filtered(lambda r: not r.reconciled and r.account_id.account_type in (
                'liability_payable', 'asset_receivable'
            ))
        debit_lines = [(0, 0, {
            'move_line_id': line.id,
            'amount': self.amount,
            'concile': True if self.payment_difference <= 0 else False,
            'full_reconcile': True if self.payment_difference <= 0 or self.payment_difference > 0 and
                self.payment_difference_handling == 'reconcile' else False,
        }) for line in lines]
        res['payment_imputation_ids'] = debit_lines or [(6, 0, [])]
        if self.payment_difference < 0:
            res['advance_amount'] = -self.payment_difference
        return res

    def _create_payment_vals_from_wizard(self, batch_result):
        values = super()._create_payment_vals_from_wizard(batch_result)
        if self._context.get('active_model') == 'account.move.line':
            values.update(
                self._get_imputation_vals(self.env['account.move.line'].browse(self._context.get('active_ids')))
            )
        return values
    
    def _create_payment_vals_from_batch(self, batch_result):
        values = super()._create_payment_vals_from_batch(batch_result)
        if self._context.get('active_model') == 'account.move.line':
            values.update(
                self._get_imputation_vals(batch_result.get('lines', []))
            )
        return values
    
    def _init_payments(self, to_process, edit_mode=False):
        res = super()._init_payments(to_process, edit_mode)
        for r in res.mapped('payment_imputation_ids'):
            r.onchange_concile()
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
