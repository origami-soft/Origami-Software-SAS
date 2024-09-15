# -*- encoding: utf-8 -*-

from odoo import fields
from odoo.exceptions import ValidationError
from .test_sold_check import TestSoldCheck


class TestWizardSellCheck(TestSoldCheck):

    def setUp(self):
        super(TestWizardSellCheck, self).setUp()
        slip_proxy = self.env['wizard.sell.check']
        third_check_proxy = self.env['account.third.check']
        date_today = fields.Date.context_today(slip_proxy)
        journal = self.journal
        journal.update_posted = True
        self.third_check_3 = third_check_proxy.create({
            'name': '12345678',
            'journal_id': self.third_check_journal.id,
            'bank_id': self.env['res.bank'].search([], limit=1).id,
            'amount': 1750,
            'currency_id': self.env.company.currency_id.id,
            'issue_date': date_today,
            'payment_date': date_today,
            'state': 'wallet',
        })
        self.third_check_4 = third_check_proxy.create({
            'name': '412414',
            'journal_id': self.third_check_journal.id,
            'bank_id': self.env['res.bank'].search([], limit=1).id,
            'amount': 750,
            'currency_id': self.env.company.currency_id.id,
            'issue_date': date_today,
            'payment_date': date_today,
            'state': 'wallet',
        })
        check_ids = [self.third_check_3.id, self.third_check_4.id]
        self.wizard_sold_check = slip_proxy.with_context(active_ids=check_ids).create({
            'journal_id': journal.id,
            'date': date_today,
            'account_id': self.env.ref('l10n_ar.1_caja_en_pesos').id,
            'commission_account_id': self.env.ref('l10n_ar.1_caja_en_pesos').id,
            'interest_account_id': self.env.ref('l10n_ar.1_caja_en_pesos').id,
            'commission': 10,
            'interests': 5
        })

    def test_create_sold_check(self):
        self.sold_check.account_third_check_ids = None
        res = self.wizard_sold_check.create_sold_check_document()
        sold_check = self.env['account.sold.check'].browse(res.get('res_id'))
        assert sold_check.date == self.wizard_sold_check.date
        assert sold_check.journal_id == self.wizard_sold_check.journal_id
        assert sold_check.amount == self.wizard_sold_check.amount
        assert sold_check.account_third_check_ids == self.third_check_3 | self.third_check_4
        assert sold_check.state == 'draft'
        assert sold_check.commission_account_id == self.wizard_sold_check.commission_account_id
        assert sold_check.interest_account_id == self.wizard_sold_check.interest_account_id
        assert sold_check.commission == self.wizard_sold_check.commission
        assert sold_check.interests == self.wizard_sold_check.interests

    def test_non_wallet_check(self):
        self.third_check_3.update({'state': 'handed'})
        self.third_check_4.update({'state': 'handed'})
        with self.assertRaises(ValidationError):
            self.wizard_sold_check.create_sold_check_document()

    def test_negative_amounts(self):
        with self.assertRaises(ValidationError):
            self.wizard_sold_check.commission = -10

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
