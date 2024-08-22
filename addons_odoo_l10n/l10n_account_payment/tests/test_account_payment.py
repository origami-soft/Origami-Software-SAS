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
from ...l10n_payment_line.exceptions.exceptions import NotEqualAmountsError


class TestAccountPayment(TransactionCase):
    def setUp(self):
        super(TestAccountPayment, self).setUp()
        self.env.company.currency_id = self.env.ref('base.ARS')

    def test_onchange_update_rates_should_update_line_rates(self):
        company = self.env.company
        usd = self.env.ref('base.USD')
        ars = self.env.ref('base.ARS')
        rate = self.env['res.currency.rate'].create({'currency_id': usd.id, 'rate': 0.1, 'company_id': company.id})
        payment = self.env['account.payment'].new({'payment_date': rate.name, 'company_id': company, 'currency_id': ars})
        line = self.env['account.payment.type.line'].new({'currency_id': usd, 'amount': 100, 'payment_id': payment})
        payment.onchange_update_rates()
        assert round(line.rate, 6) == 0.1
        assert line.payment_currency_amount == 1000

    def test_check_payment_type_line_ids_with_lines_amount_greater_than_payment_amount_should_raise_error(self):
        payment = self.env['account.payment'].new({'amount': 100, 'multiple_payment_journal': True})
        line = self.env['account.payment.type.line'].new({'payment_currency_amount': 150, 'payment_id': payment})
        with self.assertRaises(NotEqualAmountsError):
            payment.post()

    def test_validate_equal_amounts_with_lines_amount_equal_to_payment_amount_should_return_true(self):
        payment = self.env['account.payment'].new({'amount': 100, 'multiple_payment_journal': True})
        line = self.env['account.payment.type.line'].new({'payment_currency_amount': 100, 'payment_id': payment})
        assert payment.validate_equal_amounts()

    def test_validate_equal_amounts_with_lines_amount_greater_than_payment_amount_should_return_false(self):
        payment = self.env['account.payment'].new({'amount': 100, 'multiple_payment_journal': True})
        line = self.env['account.payment.type.line'].new({'payment_currency_amount': 150, 'payment_id': payment})
        assert not payment.validate_equal_amounts()

    def test_validate_equal_amounts_with_lines_amount_lower_than_payment_amount_should_return_false(self):
        payment = self.env['account.payment'].new({'amount': 100, 'multiple_payment_journal': True})
        line = self.env['account.payment.type.line'].new({'payment_currency_amount': 50, 'payment_id': payment})
        assert not payment.validate_equal_amounts()

    def test_validate_equal_amounts_with_no_lines_and_no_multiple_payment_journal_should_return_true(self):
        payment = self.env['account.payment'].new({'amount': 100})
        assert payment.validate_equal_amounts()

    def test_validate_equal_amounts_with_no_lines_should_return_false(self):
        payment = self.env['account.payment'].new({'amount': 100, 'multiple_payment_journal': True})
        assert not payment.validate_equal_amounts()

    def test_prepare_payment_moves_with_one_payment_type_line_should_return_two_moves(self):
        payment = self.env['account.payment'].new({'amount': 100, 'company_id': self.env.company, 'destination_account_id': self.env['account.account'].new()})
        line = self.env['account.payment.type.line'].new({'payment_currency_amount': 150, 'payment_id': payment, 'rate': 1.0})
        assert len(payment._prepare_payment_moves()) == 2

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
