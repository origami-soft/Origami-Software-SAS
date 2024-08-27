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


class PaymentImputationMove(models.Model):
    _name = 'payment.imputation.move'
    _description = 'Documentos imputados en un pago'

    move_id = fields.Many2one(comodel_name="account.move", string="Documento imputado", ondelete="cascade")
    invoice_date = fields.Date(related="move_id.invoice_date", string="Fecha")
    invoice_date_due = fields.Date(related="move_id.invoice_date_due", string="Fecha de vencimiento")
    amount = fields.Monetary(string="Monto imputado", compute="_compute_amounts")
    amount_residual = fields.Monetary(string="Monto restante", compute="_compute_amounts")
    amount_total = fields.Monetary(string="Total", compute="_compute_amounts")
    payment_id = fields.Many2one(comodel_name="account.payment", string="Pago", ondelete="cascade")
    currency_id = fields.Many2one(related="payment_id.currency_id")

    @api.depends("move_id", "payment_id")
    def _compute_amounts(self):
        for record in self:
            """ El método _get_reconciled_info_JSON_values es el que provee los datos
            de las imputaciones al widget de las facturas """
            reconciled_vals = record.move_id._get_reconciled_info_JSON_values()
            amount = 0
            move_currency = record.move_id.currency_id
            payment_company = record.payment_id.company_id
            payment_date = record.payment_id.payment_date
            for reconciled_value in reconciled_vals:
                """ Como puede haber más de un pago, y hasta dos veces el mismo pago
                solo tomo el importe del que concierne a la línea actual"""
                if reconciled_value.get("account_payment_id") == record.payment_id.id:
                    amount += move_currency._convert(reconciled_value.get("amount", 0.0), record.currency_id, payment_company, payment_date)
            record.update({'amount': amount,
                           'amount_residual': move_currency._convert(record.move_id.amount_residual, record.currency_id, payment_company, payment_date),
                           'amount_total': move_currency._convert(record.move_id.amount_total, record.currency_id, payment_company, payment_date)})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
