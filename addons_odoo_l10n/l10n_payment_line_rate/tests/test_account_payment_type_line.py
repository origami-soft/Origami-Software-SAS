# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo.tests.common import TransactionCase
from ..exceptions.exceptions import InvalidNaturalRateError


class TestAccountPaymentTypeLine(TransactionCase):
    def setUp(self):
        super(TestAccountPaymentTypeLine, self).setUp()

    def test_check_natural_rate_smaller_than_one_should_raise_error(self):
        line = self.env['account.payment.type.line'].new({'natural_rate': 0.5})
        with self.assertRaises(InvalidNaturalRateError):
            line.check_natural_rate()

    def test_validate_natural_rate_bigger_than_one_should_return_true(self):
        line = self.env['account.payment.type.line'].new({'natural_rate': 1.1})
        assert line.validate_natural_rate()

    def test_validate_natural_rate_one_should_return_true(self):
        line = self.env['account.payment.type.line'].new({'natural_rate': 1})
        assert line.validate_natural_rate()

    def test_validate_natural_rate_smaller_than_one_should_return_false(self):
        line = self.env['account.payment.type.line'].new({'natural_rate': 0.5})
        assert not line.validate_natural_rate()

    def test_onchange_update_rate(self):
        usd = self.env.ref('base.USD')
        company = self.env.company
        self.env['res.currency.rate'].create({'currency_id': usd.id, 'rate': 0.1})
        payment = self.env['account.payment'].new({'company_id': company})
        journal = self.env['account.journal'].new({'currency_id': usd})
        line = self.env['account.payment.type.line'].new({'payment_id': payment, 'journal_id': journal})
        line.onchange_update_rate()
        assert line.natural_rate == 10

    def test_update_natural_rate_with_real_rate_greater_than_one_and_currency_should_set_same_natural_rate(self):
        usd = self.env.ref('base.USD')
        company = self.env.company
        self.env['res.currency.rate'].create({'currency_id': usd.id, 'rate': 2})
        payment = self.env['account.payment'].new({'company_id': company})
        line = self.env['account.payment.type.line'].new({'payment_id': payment, 'currency_id': usd, 'rate': 2})
        line.update_natural_rate()
        assert line.natural_rate == 2

    def test_update_natural_rate_with_real_rate_lower_than_one_and_currency_should_set_inverted_natural_rate(self):
        company = self.env.company
        self.env['res.currency.rate'].create({'currency_id': self.env.ref('base.USD').id, 'rate': 0.25})
        payment = self.env['account.payment'].new({'company_id': company})
        line = self.env['account.payment.type.line'].new({'payment_id': payment, 'currency_id': self.env.ref('base.USD'), 'rate': 0.25})
        line.update_natural_rate()
        assert line.natural_rate == 4

    def test_update_natural_rate_with_real_rate_greater_than_one_and_no_currency_should_set_zero_natural_rate(self):
        usd = self.env.ref('base.USD')
        company = self.env.company
        self.env['res.currency.rate'].create({'currency_id': usd.id, 'rate': 0.25})
        payment = self.env['account.payment'].new({'company_id': company})
        line = self.env['account.payment.type.line'].new({'payment_id': payment, 'rate': 0.25})
        line.update_natural_rate()
        assert not line.natural_rate

    def test_onchange_natural_rate_with_real_rate_greater_than_one_and_currency_should_set_same_natural_rate(self):
        usd = self.env.ref('base.USD')
        company = self.env.company
        self.env['res.currency.rate'].create({'currency_id': usd.id, 'rate': 2})
        payment = self.env['account.payment'].new({'company_id': company})
        line = self.env['account.payment.type.line'].new({'payment_id': payment, 'currency_id': usd, 'natural_rate': 2})
        line.onchange_natural_rate()
        assert line.rate == 2

    def test_onchange_natural_rate_with_real_rate_lower_than_one_and_currency_should_set_inverted_natural_rate(self):
        usd = self.env.ref('base.USD')
        company = self.env.company
        self.env['res.currency.rate'].create({'currency_id': self.env.ref('base.USD').id, 'rate': 0.25})
        payment = self.env['account.payment'].new({'company_id': company})
        line = self.env['account.payment.type.line'].new({'payment_id': payment, 'currency_id': self.env.ref('base.USD'), 'natural_rate': 4})
        line.onchange_natural_rate()
        assert line.rate == 0.25

    def test_onchange_natural_rate_with_real_rate_greater_than_one_and_no_currency_should_set_zero_natural_rate(self):
        usd = self.env.ref('base.USD')
        company = self.env.company
        self.env['res.currency.rate'].create({'currency_id': usd.id, 'rate': 0.25})
        payment = self.env['account.payment'].new({'company_id': company})
        line = self.env['account.payment.type.line'].new({'payment_id': payment, 'natural_rate': 4})
        line.onchange_natural_rate()
        assert not line.rate

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
