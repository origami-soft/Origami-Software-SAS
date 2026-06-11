# -*- encoding: utf-8 -*-

from odoo import models, api
from collections import defaultdict


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def do_partial_reconcile_with_exchange_difference(self, debit_move, credit_move, amount):
        """ Armo una conciliación parcial entre dos apuntes por el importe solicitado, pero generando un asiento de
        diferencia de cambio en los casos que esté tratando con monedas (Odoo base recién hace el asiento de diferencia
        en la conciliación que termina de cancelar el apunte)
        """
        debit_vals = {
            'aml': debit_move,
            'amount_residual': amount * debit_move.get_move_line_rate(),
            'amount_residual_currency': amount
        }
        credit_vals = {
            'aml': credit_move,
            'amount_residual': -amount * credit_move.get_move_line_rate(),
            'amount_residual_currency': -amount
        }
        results = self._prepare_reconciliation_single_partial(debit_vals, credit_vals)
        if results.get('exchange_values'):
            exchange_move = self._create_exchange_difference_moves([results['exchange_values']])
        else:
            exchange_move = False
        partial = self.env['account.partial.reconcile'].create(results['partial_values'])
        if exchange_move:
            partial.exchange_move_id = exchange_move
            exchange_move_line = exchange_move.line_ids.filtered(lambda l: l.account_id == debit_move.account_id)
            # Puede darse el caso de que no concilie la diferencia de cambio si la cotización del crédito que se usó es
            # inferior a la del débito que se está saldando. En esos casos fuerzo la conciliación.
            if not exchange_move_line.reconciled:
                (exchange_move_line | debit_move | credit_move).reconcile()

    def get_move_line_rate(self):
        """Método auxiliar para obtener la cotización utilizada en
        un account.move.line en particular

        :return: Monto convertido
        :rtype: float
        """
        if not self.currency_id or self.currency_id == self.company_currency_id:
            return 1
        return self.balance / self.amount_currency

    @api.model
    def _create_exchange_difference_moves(self, exchange_diff_values_list):
        """ Puede que en algunos casos borde de imputaciones (ej.: el que motivó este ajuste fue una factura cancelada
        parcialmente con una nota de crédito de cotización distinta que generó una dif de cambio, para que luego su
        restante se cancele con un cobro con la misma cotización de la factura que incluye importe a cuenta) Odoo
        intente generar un asiento de diferencia de cambio que tiene más apuntes (ej.: 4) y donde todos se cancelan
        entre sí, lo cual puede llevar a problemas a la hora de conciliar los apuntes imputados contra los del pago.
        Por lo tanto, si estamos en un caso así (definido por aquellos donde el balance de todas las cuentas
        involucradas es 0), directamente no generamos ningún asiento.
        """
        balance_by_account = defaultdict(float)
        for vals_list in exchange_diff_values_list:
            aml_vals = vals_list.get('move_values', {}).get('line_ids', [])
            for command, _, vals in aml_vals:
                balance_by_account[vals['account_id']] += round(vals['debit'], 2) - round(vals['credit'], 2)
        if not any(v for v in balance_by_account.values()):
            return []
        return super()._create_exchange_difference_moves(exchange_diff_values_list)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
