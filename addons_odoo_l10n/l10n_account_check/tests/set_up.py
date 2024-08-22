# -*- encoding: utf-8 -*-

from odoo.tests import common
from odoo import fields


class SetUp(common.TransactionCase):
    def _create_payments(self):
        self.partner = self.env['res.partner'].create({
            'name': 'Partner',
        })
        self.customer_payment = self.env['account.payment'].create({
            'partner_id': self.partner.id,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
            'amount': 500
        })
        self.supplier_payment = self.env['account.payment'].create({
            'partner_id': self.partner.id,
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'payment_method_id': self.env.ref('account.account_payment_method_manual_out').id,
            'amount': 500
        })

    def _create_checks(self):
        third_check_proxy = self.env['account.third.check']
        date_today = fields.Date.context_today(third_check_proxy)
        self.third_check = self.env['account.third.check'].create({
            'name': '12345678',
            'bank_id': self.env['res.bank'].search([], limit=1).id,
            'payment_type': 'common',
            'amount': 1300,
            'currency_id': self.env.company.currency_id.id,
            'issue_date': date_today,
            'payment_date': date_today
        })

    def setUp(self):
        super(SetUp, self).setUp()
        self._create_payments()
        self._create_checks()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
