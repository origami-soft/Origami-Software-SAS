# -*- encoding: utf-8 -*-

from odoo import fields
from odoo.exceptions import ValidationError
from .test_sold_check import TestSoldCheck


class TestAccountThirdCheck(TestSoldCheck):

    def test_sold_check_id(self):
        self.sold_check.post()
        assert self.third_check.sold_check_id == self.sold_check

    def test_invalid_third_check_state(self):
        self.third_check.state = 'draft'
        with self.assertRaises(ValidationError):
            self.third_check.sold_check_contraints()

    def test_multiple_sold_checks(self):
        sold_check = self.env['account.sold.check'].new({
            'journal_id': self.sold_check.journal_id,
            'date': fields.Date.context_today(self.env['account.sold.check']),
            'account_third_check_ids': self.third_check,
            'account_id': self.env.ref('l10n_ar.1_caja_en_pesos')
        })
        with self.assertRaises(ValidationError):
            self.third_check.sold_check_contraints()

    def test_invalid_check_state_post(self):
        self.third_check.state = 'draft'
        with self.assertRaises(ValidationError):
            self.sold_check.post()

    def test_invalid_check_currency_post(self):
        usd = self.env.ref('base.USD')
        self.third_check.currency_id = usd
        third_checks = self.third_check | self.third_check_2
        with self.assertRaises(ValidationError):
            third_checks.post_sold_check()

    def test_invalid_check_state_cancel(self):
        self.third_check.state = 'draft'
        with self.assertRaises(ValidationError):
            self.sold_check.cancel()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
