# -*- encoding: utf-8 -*-

from odoo import models, api
from collections import defaultdict


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

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
