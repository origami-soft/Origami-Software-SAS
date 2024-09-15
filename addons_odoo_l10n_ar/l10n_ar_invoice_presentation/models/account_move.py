# -*- encoding: utf-8 -*-

from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def get_currency_rate_from_move(self):
        """
        Obtiene la cotización de la factura, que será 1 ya que las facturas se presentan en la moneda correspondiente.
        :param invoice: record, factura
        :return: la cotización
        :rtype: float
        """
        # Traemos todas las lineas del asiento que tengan esa cuenta
        move_lines = self.line_ids.filtered(
            lambda x: x.account_id.account_type in ('asset_receivable', 'liability_payable') and (
                        x.amount_currency or x.balance)) or self.line_ids.filtered(
            lambda x: x.amount_currency) or self.line_ids.filtered(lambda l: l.balance)
        move_line = move_lines[0]
        # Traemos el monto de la linea, si es de debito o credito
        amount = move_line.credit or move_line.debit
        amount_currency = abs(move_line.amount_currency)
        # El rate sera el monto dividido la currency si es distinto de cero, sino se divide por si mismo
        currency_rate = float(amount) / float(amount_currency or amount)
        return currency_rate

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
