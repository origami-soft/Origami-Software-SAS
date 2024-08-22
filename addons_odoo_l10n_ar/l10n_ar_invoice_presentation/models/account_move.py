# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api


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
            lambda x: x.account_id.user_type_id.type in ('receivable', 'payable') and (
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
