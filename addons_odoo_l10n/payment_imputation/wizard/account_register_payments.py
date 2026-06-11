# -*- encoding: utf-8 -*-

from odoo import models


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def _get_imputation_line_amount(self, line):
        self.ensure_one()
        if not line.move_id.payment_id and not line.move_id.statement_line_id:
            conversion_date = self.payment_date
        else:
            conversion_date = line.date
        amount = self.company_id.currency_id._convert(
            line.amount_residual,
            self.currency_id,
            self.company_id,
            conversion_date,
        )
        return abs(amount)

    def _get_imputation_vals(self, orig_lines):
        res = {}
        lines = self.env['account.move.line']
        for line in orig_lines:
            lines |= line.filtered(lambda r: not r.reconciled and r.account_id.account_type in (
                'liability_payable', 'asset_receivable'
            ))
        # En caso de que se esté imputando un solo apunte, armo una imputación común con el importe del wizard
        if len(lines) <= 1:
            debit_lines = [(0, 0, {
                'move_line_id': line.id,
                'amount': self.amount,
                'concile': True if self.payment_difference <= 0 else False,
                'full_reconcile': True if self.payment_difference <= 0 or self.payment_difference > 0 and
                    self.payment_difference_handling == 'reconcile' else False,
            }) for line in lines]
        # Si se está imputando más de un apunte (en facturas con plazos de pago compuestos), voy convirtiendo a la
        # moneda que corresponda y descontando del importe del wizard hasta que ya no quede nada
        else:
            remaining_amount = self.amount or sum(self._get_imputation_line_amount(l) for l in lines)
            debit_lines = []
            for line in lines:
                imputation_amount = self._get_imputation_line_amount(line)
                real_amount = min(imputation_amount, remaining_amount)  # Para evitar armar imputaciones que sobrepasen el total del pago
                remaining_amount -= real_amount
                debit_lines.append((0, 0, {
                    'move_line_id': line.id,
                    'amount': real_amount,
                    'concile': True if self.payment_difference <= 0 else False,
                    'full_reconcile': True if self.payment_difference <= 0 or self.payment_difference > 0 and
                        self.payment_difference_handling == 'reconcile' else False,
                }))
                if remaining_amount <= 0:
                    break

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
