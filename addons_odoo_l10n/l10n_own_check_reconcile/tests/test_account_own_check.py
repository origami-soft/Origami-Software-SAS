# -*- encoding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo import fields


class TestAccountOwnCheck(TransactionCase):
    def create_check(self):
        bank = self.env['res.bank'].new({
            'name': "Banco ejemplo",
        })
        journal = self.env['account.journal'].new({'bank_id': bank.id})

        self.check = self.env['account.own.check'].new({
            'bank_id': bank.id,
            'name': "123456",
            'check_type': 'common',
            'payment_date': fields.Date.today(),
            'issue_date': fields.Date.today(),
            'state': 'handed',
            'destination_payment_id': self.env['account.payment'].new({}),
        })

    def setUp(self):
        super(TestAccountOwnCheck, self).setUp()
        self.create_check()

    def test_reconcile(self):
        self.check.reconcile_check({})
        assert self.check.state == 'reconciled'

    def test_reconcile_invalid_state(self):
        self.check.state = 'draft'
        with self.assertRaises(ValidationError):
            self.check.reconcile_check({})

    def test_cancel_reconcile(self):
        self.check.reconcile_check({})
        self.check.cancel_reconcile()
        assert self.check.state == 'handed'

    def test_cancel_reconcile_error(self):
        self.check.reconcile_check({})
        self.check.destination_payment_id = None
        with self.assertRaises(ValidationError):
            self.check.cancel_reconcile()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
