# -*- encoding: utf-8 -*-

from odoo import models


class AccountInvoicePerception(models.Model):
    _inherit = 'account.invoice.perception'

    def get_report_document_tax_data(self):
        perceptions = []
        for perception in self:
            currency_rate = self.env['perception.sifere']._get_invoice_currency_rate(perception.move_id)
            perceptions.append({
                'date': perception.date_account,
                'name': perception.name,
                'partner': perception.partner_id.name,
                'document_number': perception.partner_id.vat,
                'origin': perception.move_id.display_name,
                'origin_amount': round(perception.move_id.amount_total_signed, 2),
                'taxable_base': round(perception.base * currency_rate, 2),
                'aliquot': round((perception.amount / perception.base) * 100 if perception.base else 0.0, 2),
                'amount': round(perception.amount * currency_rate, 2),
            })
        return perceptions

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
