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
from ..exceptions.exceptions import NoAccountError, InvalidAmountError, InvalidRateError
from datetime import date


class TestAccountAbstractPaymentLine(TransactionCase):
    def setUp(self):
        super(TestAccountAbstractPaymentLine, self).setUp()
        self.env.company.currency_id = self.env.ref('base.ARS')

    def test_check_journal_id_inbound_payment_and_journal_without_debit_account_should_raise_error(self):
        payment = self.env['account.payment'].new({'payment_type': 'inbound'})
        journal = self.env['account.journal'].new()
        line = self.env['account.abstract.payment.line'].new({'payment_id': payment, 'journal_id': journal})
        with self.assertRaises(NoAccountError):
            assert not line.check_journal_id()

    def test_validate_journal_accounts_inbound_payment_and_journal_with_debit_account_should_return_true(self):
        payment = self.env['account.payment'].new({'payment_type': 'inbound'})
        journal = self.env['account.journal'].new({'default_debit_account_id': self.env['account.account'].new()})
        line = self.env['account.abstract.payment.line'].new({'payment_id': payment, 'journal_id': journal})
        assert line.validate_journal_accounts()

    def test_validate_journal_accounts_inbound_payment_and_journal_without_debit_account_should_return_false(self):
        payment = self.env['account.payment'].new({'payment_type': 'inbound'})
        journal = self.env['account.journal'].new()
        line = self.env['account.abstract.payment.line'].new({'payment_id': payment, 'journal_id': journal})
        assert not line.validate_journal_accounts()

    def test_validate_journal_accounts_outbound_payment_and_journal_with_credit_account_should_return_true(self):
        payment = self.env['account.payment'].new({'payment_type': 'outbound'})
        journal = self.env['account.journal'].new({'default_credit_account_id': self.env['account.account'].new()})
        line = self.env['account.abstract.payment.line'].new({'payment_id': payment, 'journal_id': journal})
        assert line.validate_journal_accounts()

    def test_validate_journal_accounts_outbound_payment_and_journal_without_credit_account_should_return_false(self):
        payment = self.env['account.payment'].new({'payment_type': 'outbound'})
        journal = self.env['account.journal'].new()
        line = self.env['account.abstract.payment.line'].new({'payment_id': payment, 'journal_id': journal})
        assert not line.validate_journal_accounts()

    def test_get_journal_currency_journal_with_different_currency_than_company_should_set_journal_currency(self):
        company = self.env['res.company'].new({'currency_id': self.env.ref('base.ARS')})
        payment = self.env['account.payment'].new({'company_id': company})
        journal = self.env['account.journal'].new({'currency_id': self.env.ref('base.USD')})
        line = self.env['account.abstract.payment.line'].new({'payment_id': payment, 'journal_id': journal})
        line.get_journal_currency()
        assert line.currency_id == self.env.ref('base.USD')

    def test_get_journal_currency_journal_with_same_currency_than_company_should_set_journal_currency(self):
        company = self.env['res.company'].new({'currency_id': self.env.ref('base.ARS')})
        payment = self.env['account.payment'].new({'company_id': company})
        journal = self.env['account.journal'].new({'currency_id': self.env.ref('base.ARS')})
        line = self.env['account.abstract.payment.line'].new({'payment_id': payment, 'journal_id': journal})
        line.get_journal_currency()
        assert line.currency_id == self.env.ref('base.ARS')

    def test_get_journal_currency_journal_with_no_currency_should_set_company_currency(self):
        company = self.env['res.company'].new({'currency_id': self.env.ref('base.ARS')})
        payment = self.env['account.payment'].new({'company_id': company})
        journal = self.env['account.journal'].new()
        line = self.env['account.abstract.payment.line'].new({'payment_id': payment, 'journal_id': journal})
        line.get_journal_currency()
        assert line.currency_id == self.env.ref('base.ARS')

    def test_get_journal_currency_no_journal_should_set_false(self):
        payment = self.env['account.payment'].new()
        payment.company_id.currency_id = self.env.ref('base.ARS')
        line = self.env['account.abstract.payment.line'].new({'payment_id': payment})
        line.get_journal_currency()
        assert not line.currency_id

    def test_onchange_update_rate_when_currencies_set_should_set_new_rate(self):
        self.env['res.currency.rate'].create({'currency_id': self.env.ref('base.USD').id, 'rate': 0.1})
        company = self.env.company
        payment = self.env['account.payment'].new({'company_id': company})
        journal = self.env['account.journal'].new({'currency_id': self.env.ref('base.USD')})
        line = self.env['account.abstract.payment.line'].new({'payment_id': payment, 'journal_id': journal})
        line.onchange_update_rate()
        assert round(line.rate, 6) == 0.1

    def test_onchange_update_rate_when_no_currencies_set_should_clear_data(self):
        line = self.env['account.abstract.payment.line'].new()
        line.rate = 1.0
        line.onchange_update_rate()
        assert not line.rate

    def test_onchange_update_rate_when_do_not_update_rates_in_context_should_make_no_changes(self):
        self.env['res.currency.rate'].create({'currency_id': self.env.ref('base.USD').id, 'rate': 0.1})
        company = self.env.company
        payment = self.env['account.payment'].new({'company_id': company})
        journal = self.env['account.journal'].new({'currency_id': self.env.ref('base.USD')})
        line = self.env['account.abstract.payment.line'].new({'payment_id': payment, 'journal_id': journal})
        line.rate = 1.0
        line.with_context(do_not_update_rates=True).onchange_update_rate()
        assert line.rate == 1.0

    def test_onchange_amount_should_update_payment_currency_amount(self):
        company = self.env.company
        payment = self.env['account.payment'].new({'company_id': company, 'payment_date': date.today()})
        line = self.env['account.abstract.payment.line'].new({
            'payment_id': payment,
            'rate': 0.1,
            'payment_currency_id': self.env.ref('base.ARS'),
            'currency_id': self.env.ref('base.USD'),
            'amount': 50
        })
        line.onchange_amount()
        assert line.payment_currency_amount == 500

    def test_onchange_payment_currency_amount_should_update_amount(self):
        company = self.env.company
        payment = self.env['account.payment'].new({'company_id': company, 'payment_date': date.today()})
        line = self.env['account.abstract.payment.line'].new({
            'payment_id': payment,
            'rate': 0.1,
            'payment_currency_id': self.env.ref('base.ARS'),
            'currency_id': self.env.ref('base.USD'),
            'amount': 25,
            'payment_currency_amount': 50,
        })
        line.onchange_payment_currency_amount()
        assert line.rate == 0.5

    def test_check_amount_negative_should_raise_error(self):
        line = self.env['account.abstract.payment.line'].new({'amount': -0.1})
        with self.assertRaises(InvalidAmountError):
            line.check_amount()

    def test_validate_amount_positive_should_return_true(self):
        line = self.env['account.abstract.payment.line'].new({'amount': 0.1})
        assert line.validate_amount()

    def test_validate_amount_zero_should_return_false(self):
        line = self.env['account.abstract.payment.line'].new({'amount': 0})
        assert not line.validate_amount()

    def test_validate_amount_negative_should_return_false(self):
        line = self.env['account.abstract.payment.line'].new({'amount': -0.1})
        assert not line.validate_amount()

    def test_check_rate_negative_should_raise_error(self):
        line = self.env['account.abstract.payment.line'].new({'rate': -0.1})
        with self.assertRaises(InvalidRateError):
            line.check_rate()

    def test_validate_rate_positive_should_return_true(self):
        line = self.env['account.abstract.payment.line'].new({'rate': 0.1})
        assert line.validate_rate()

    def test_validate_rate_zero_should_return_false(self):
        line = self.env['account.abstract.payment.line'].new({'rate': 0})
        assert not line.validate_rate()

    def test_validate_rate_negative_should_return_false(self):
        line = self.env['account.abstract.payment.line'].new({'rate': -0.1})
        assert not line.validate_rate()

    def test_get_move_vals_on_outbound_payment_with_valid_line_should_return_values_dictionary(self):
        today = date.today()
        usd = self.env.ref('base.USD')
        ars = self.env.ref('base.ARS')
        debit_account_1 = self.env['account.account'].new()
        credit_account_1 = self.env['account.account'].new()
        debit_account_2 = self.env['account.account'].new()
        credit_account_2 = self.env['account.account'].new()
        company = self.env.company
        commercial_partner = self.env['res.partner'].new()
        partner = self.env['res.partner'].new({'commercial_partner_id': commercial_partner})
        journal = self.env['account.journal'].new({
            'currency_id': ars,
            'name': "Diario de pago",
            'default_debit_account_id': debit_account_1,
            'default_credit_account_id': credit_account_1
        })
        payment = self.env['account.payment'].new({
            'company_id': company,
            'payment_date': today,
            'communication': "Ejemplo",
            'payment_type': 'outbound',
            'currency_id': ars,
            'partner_id': partner,
            'journal_id': journal,
            'name': "P0001"
        })
        line_journal = self.env['account.journal'].new({
            'currency_id': usd,
            'name': "Método ejemplo",
            'default_debit_account_id': debit_account_2,
            'default_credit_account_id': credit_account_2
        })
        line = self.env['account.abstract.payment.line'].new({
            'payment_id': payment,
            'journal_id': line_journal,
            'currency_id': usd,
            'rate': 0.1,
            'amount': 50,
            'payment_currency_amount': 500,
        })
        res = line.get_move_vals(payment)
        assert res == {
            'date': today,
            'ref': "Ejemplo",
            'journal_id': line_journal.id,
            'currency_id': self.env.ref('base.USD').id,
            'partner_id': partner.id,
            'line_ids': [
                (0, 0, {
                    'name': "Método ejemplo",
                    'amount_currency': -50.0,
                    'currency_id': usd.id,
                    'debit': 0.0,
                    'credit': 500.0,
                    'date_maturity': today,
                    'partner_id': commercial_partner.id,
                    'account_id': credit_account_2.id,
                    'payment_id': payment.id,
                }),
                (0, 0, {
                    'name': "P0001",
                    'amount_currency': 0.0,
                    'currency_id': False,
                    'debit': 500.0,
                    'credit': 0.0,
                    'date_maturity': today,
                    'partner_id': commercial_partner.id,
                    'account_id': debit_account_1.id,
                    'payment_id': payment.id,
                }),
            ],
        }

    def test_get_move_vals_on_inbound_payment_with_valid_line_should_return_values_dictionary(self):
        today = date.today()
        ars = self.env.ref('base.ARS')
        debit_account_1 = self.env['account.account'].new()
        credit_account_1 = self.env['account.account'].new()
        debit_account_2 = self.env['account.account'].new()
        credit_account_2 = self.env['account.account'].new()
        company = self.env.company
        commercial_partner = self.env['res.partner'].new()
        partner = self.env['res.partner'].new({'commercial_partner_id': commercial_partner})
        journal = self.env['account.journal'].new({
            'currency_id': ars,
            'name': "Diario de pago",
            'default_debit_account_id': debit_account_1,
            'default_credit_account_id': credit_account_1
        })
        payment = self.env['account.payment'].new({
            'company_id': company,
            'payment_date': today,
            'communication': "Ejemplo",
            'payment_type': 'inbound',
            'currency_id': ars,
            'partner_id': partner,
            'journal_id': journal,
            'name': "P0001"
        })
        line_journal = self.env['account.journal'].new({
            'currency_id': ars,
            'name': "Método ejemplo",
            'default_debit_account_id': debit_account_2,
            'default_credit_account_id': credit_account_2
        })
        line = self.env['account.abstract.payment.line'].new({
            'payment_id': payment,
            'journal_id': line_journal,
            'currency_id': ars,
            'rate': 1.0,
            'amount': 50,
            'payment_currency_amount': 50
        })
        res = line.get_move_vals(payment)
        assert res == {
            'date': today,
            'ref': "Ejemplo",
            'journal_id': line_journal.id,
            'currency_id': ars.id,
            'partner_id': partner.id,
            'line_ids': [
                (0, 0, {
                    'name': "Método ejemplo",
                    'amount_currency': 0.0,
                    'currency_id': False,
                    'debit': 50.0,
                    'credit': 0.0,
                    'date_maturity': today,
                    'partner_id': commercial_partner.id,
                    'account_id': debit_account_2.id,
                    'payment_id': payment.id,
                }),
                (0, 0, {
                    'name': "P0001",
                    'amount_currency': 0.0,
                    'currency_id': False,
                    'debit': 0.0,
                    'credit': 50.0,
                    'date_maturity': today,
                    'partner_id': commercial_partner.id,
                    'account_id': credit_account_1.id,
                    'payment_id': payment.id,
                }),
            ],
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
