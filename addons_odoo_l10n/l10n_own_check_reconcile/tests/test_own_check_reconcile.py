# -*- encoding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import date


class TestOwnCheckReconcile(TransactionCase):
    def create_account_type(self):
        self.account_type = self.env['account.account.type'].create({
            'name': "Ejemplo",
        })

    def create_journal(self):
        self.journal = self.env['account.journal'].create({
            'code': "EJE",
            'name': "Ejemplo",
            'user_type_id': self.account_type.id,
            'type': 'cash',
            'update_posted': True,
        })

    def create_account(self):
        self.account = self.env['account.account'].create({
            'code': "Codigo",
            'name': "Cuenta",
            'user_type_id': self.account_type.id,
        })

    def create_check(self):
        bank = self.env['res.bank'].new({
            'name': "Banco ejemplo",
        })
        journal = self.env['account.journal'].new({'update_posted': True, 'bank_id': bank.id})

        self.check = self.env['account.own.check'].create({
            'bank_id': bank.id,
            'currency_id': self.env.ref('base.ARS').id,
            'name': "123456",
            'check_type': 'common',
            'amount': 500,
            'payment_date': date.today(),
            'issue_date': date.today(),
            'state': 'handed',
        })

    def create_reconcile_and_lines(self):
        self.reconcile = self.env['own.check.reconcile'].new({
            'journal_id': self.journal.id,
        })
        self.reconcile.line_ids = self.with_context(active_ids=[self.check.id])._get_lines()
        self.reconcile.line_ids.update({'account_id': self.account.id})

    def setUp(self):
        super(TestOwnCheckReconcile, self).setUp()
        self.create_account_type()
        self.create_journal()
        self.create_account()
        self.create_move()
        self.create_check()
        self.create_reconcile_and_lines()

    def test_validate_lines(self):
        self.check.state = 'draft'
        with self.assertRaises(ValidationError):
            self.reconcile.validate_lines(self.reconcile.line_ids.ids)

    def test_reconcile(self):
        self.reconcile.confirm()
        assert self.reconcile.move_id
        assert self.reconcile.state == 'confirmed'
        assert self.check.state == 'reconciled'
        assert self.check.reconcile_id == self.reconcile
        assert sum(self.reconcile.move_id.line_ids.mapped('debit')) == 500
        assert sum(self.reconcile.move_id.line_ids.mapped('credit')) == 500

    def test_cancel(self):
        self.reconcile.confirm()
        move = self.reconcile.move_id
        self.reconcile.cancel()
        assert self.check.state == 'handed'
        assert not self.reconcile.move_id
        assert self.reconcile.state == 'canceled'
        assert not self.check.reconcile_id
        assert not move.exists()

    def test_reconcile_multi(self):
        usd = self.env.ref('base.USD')
        self.check.currency_id = usd
        self.env['res.currency.rate'].create({
            'currency_id': usd.id,
            'rate': 0.1
        })
        self.reconcile.confirm()
        assert self.reconcile.move_id
        assert self.check.state == 'reconciled'
        assert self.check.reconcile_id == self.reconcile
        assert sum(self.reconcile.move_id.line_ids.mapped('debit')) == 5000
        assert sum(self.reconcile.move_id.line_ids.mapped('credit')) == 5000
        assert sum(abs(v) for v in self.reconcile.move_id.line_ids.mapped('amount_currency')) == 1000
        assert all(l.currency_id == usd for l in self.reconcile.move_id.line_ids)

    def test_confirm_no_account(self):
        self.reconcile.line_ids.update({'account_id': False})
        with self.assertRaises(ValidationError):
            self.reconcile.confirm()

    def test_confirm_no_lines(self):
        self.reconcile.line_ids.unlink()
        with self.assertRaises(ValidationError):
            self.reconcile.confirm()

    def test_dont_unlink_if_confirmed(self):
        self.reconcile.state = 'confirmed'
        with self.assertRaises(ValidationError):
            self.reconcile.unlink()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
