# -*- encoding: utf-8 -*-

from odoo import models


class AccountPaymentRetention(models.Model):
    _inherit = 'account.payment.retention'

    def _get_report_document_tax_dict(self):
        return {
            'date': self.payment_date,
            'name': self.certificate_no,
            'partner': self.partner_id.name,
            'document_number': self.partner_id.vat,
            'origin': self.payment_id.display_name,
            'origin_amount': round(self.payment_id.amount, 2),
            'taxable_base': round(self.base, 2),
            'aliquot': round((self.amount/self.base) * 100 if self.base else 0.0, 2),
            'amount': round(self.amount, 2),
        }

    def get_report_document_tax_data(self):
        return [retention._get_report_document_tax_dict() for retention in self]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
