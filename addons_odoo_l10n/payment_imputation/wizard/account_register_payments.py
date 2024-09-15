# -*- encoding: utf-8 -*-

from odoo import models


class AccountPaymentRegister(models.TransientModel):

    _inherit = 'account.payment.register'

    def _create_payment_vals_from_wizard(self, batch_result):
        values = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard(batch_result)
        if self._context.get('active_model') == 'account.move.line' and not self.can_group_payments:
            lines = self.env['account.move.line']
            for line in lines.browse(self._context.get('active_ids')):
                lines |= line.filtered(
                    lambda r: not r.reconciled and r.account_id.account_type in (
                        'liability_payable', 'asset_receivable'
                    )
                )
            debit_lines = [(0, 0, {
                'move_line_id': line.id,
                'amount': self.amount,
                'concile': True if not self.payment_difference else False,
                'full_reconcile': True if not self.payment_difference or self.payment_difference and
                self.payment_difference_handling == 'reconcile' else False,
            }) for line in lines]
            values['payment_imputation_ids'] = debit_lines or [(6, 0, [])]
        return values

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
