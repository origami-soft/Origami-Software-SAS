# -*- encoding: utf-8 -*-

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
            # El método _get_reconciled_info_JSON_values es el que provee los datos de las conciliaciones hechas
            reconciled_vals = record.move_id._get_all_reconciled_invoice_partials()
            payment_company = record.payment_id.company_id
            payment_date = record.payment_id.date
            amount = 0
            for val in reconciled_vals:
                # Si lo que se está conciliando contra la factura no es el pago del documento imputado, lo ignoro
                if not val.get('aml') or val['aml'].payment_id != record.payment_id:
                    continue
                amount += val['currency']._convert(val.get("amount", 0.0), record.currency_id, payment_company, payment_date)

            move_currency = record.move_id.currency_id
            record.update({
                'amount': amount,
                'amount_residual': move_currency._convert(record.move_id.amount_residual, record.currency_id, payment_company, payment_date),
                'amount_total': move_currency._convert(record.move_id.amount_total, record.currency_id, payment_company, payment_date)
            })

    def open_move(self):
        view_form = self.env.ref('account.view_move_form').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Factura',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': self.move_id.id,
            'view_id': view_form,
            'context': "{'create': False}",
            'target': 'current'
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
