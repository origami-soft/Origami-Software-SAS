# -*- encoding: utf-8 -*-

from odoo.tests import common
from odoo import fields
from odoo.exceptions import ValidationError


class TestAccountThirdCheck(common.TransactionCase):

    def setUp(self):
        super(TestAccountThirdCheck, self).setUp()
        third_check_proxy = self.env['account.third.check']
        date_today = fields.Date.context_today(third_check_proxy)
        bank = self.env['res.bank'].new()
        payment = self.env['account.payment'].new({
            'state': 'posted',
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
            'amount': 23
        })
        deposit_slip = self.env['account.deposit.slip'].new({
            'journal_id': journal.id,
            'date': fields.Date.context_today(self.env['account.deposit.slip']),
        })
        self.third_check_wallet = self.env['account.third.check'].new({
            'name': '12345678',
            'bank_id': bank,
            'check_type': 'common',
            'amount': 1300,
            'currency_id': self.env.company.currency_id.id,
            'issue_date': date_today,
            'payment_date': date_today,
            'state': 'wallet'
        })
        self.third_check_handed = self.env['account.third.check'].new({
            'name': '5125125',
            'bank_id': bank,
            'check_type': 'postdated',
            'amount': 252,
            'currency_id': self.env.company.currency_id.id,
            'issue_date': date_today,
            'payment_date': date_today,
            'state': 'handed',
            'account_payment_ids': [(6, 0, [payment.id])]
        })
        self.third_check_deposited = self.env['account.third.check'].new({
            'name': '5125125',
            'bank_id': bank,
            'check_type': 'postdated',
            'amount': 252,
            'currency_id': self.env.company.currency_id.id,
            'issue_date': date_today,
            'payment_date': date_today,
            'state': 'wallet',
            'deposit_slip_ids': [(6, 0, [deposit_slip.id])]
        })
        self.third_check_deposited.post_deposit_slip()
        self.third_checks = self.third_check_wallet | self.third_check_handed | self.third_check_deposited

    def test_reject_check(self):
        self.third_checks.reject_check()
        assert all(check == 'rejected' for check in self.third_checks.mapped("state"))

    def test_button_reject_check(self):
        self.third_checks.button_reject_check()
        assert all(check == 'rejected' for check in self.third_checks.mapped("state"))

    def test_invalid_reject_check(self):
        self.third_check_handed.state = 'draft'
        with self.assertRaises(ValidationError):
            self.third_checks.reject_check()

    def test_revert_check(self):
        """ Cada cheque deberia tener su estado original """
        self.third_checks.reject_check()
        self.third_checks.revert_reject()
        assert self.third_check_wallet.state == 'wallet'
        assert self.third_check_handed.state == 'handed'
        assert self.third_check_deposited.state == 'deposited'

    def test_button_revert_check(self):
        self.third_checks.reject_check()
        self.third_checks.button_revert_reject()
        assert self.third_check_wallet.state == 'wallet'
        assert self.third_check_handed.state == 'handed'
        assert self.third_check_deposited.state == 'deposited'

    def test_invalid_revert_check(self):
        with self.assertRaises(ValidationError):
            self.third_checks.revert_reject()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
