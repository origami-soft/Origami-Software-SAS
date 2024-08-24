# -*- encoding: utf-8 -*-

from odoo import models


class AccountPaymentRetention(models.Model):
    _inherit = 'account.payment.retention'

    def get_report_document_tax_data(self):
        return [{
            'date': retention.payment_date,
            'name': retention.certificate_no,
            'partner': retention.partner_id.name,
            'document_number': retention.partner_id.vat,
            'origin': retention.payment_id.display_name,
            'origin_amount': round(retention.payment_id.amount, 2),
            'taxable_base': round(retention.base, 2),
            'aliquot': round((retention.amount/retention.base) * 100 if retention.base else 0.0, 2),
            'amount': round(retention.amount, 2),

        } for retention in self]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
