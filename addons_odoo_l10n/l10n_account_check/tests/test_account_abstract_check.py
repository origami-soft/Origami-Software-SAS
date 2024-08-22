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
from odoo import fields
from dateutil.relativedelta import relativedelta
from mock import mock
from ..exceptions.exceptions import NonNumericCheckError, InvalidCheckAmountError, InvalidCheckDatesError,\
    NotEqualCheckDatesError, CancelPaymentNonHandedCheckError, InvalidCheckCancelStateError, InvalidCheckNextStateError


class TestAccountAbstractCheck(TransactionCase):
    def setUp(self):
        super(TestAccountAbstractCheck, self).setUp()

    def test_check_name_all_digits_should_return_true(self):
        check = self.env['account.abstract.check'].new({'name': "0001"})
        assert check._check_name()

    def test_check_name_not_all_digits_should_return_false(self):
        check = self.env['account.abstract.check'].new({'name': "0001A"})
        assert not check._check_name()

    def test_check_name_empty_should_return_false(self):
        check = self.env['account.abstract.check'].new({'name': ""})
        assert not check._check_name()

    def test_constraint_name_empty_should_raise_error(self):
        check = self.env['account.abstract.check'].new({'name': ""})
        with self.assertRaises(NonNumericCheckError):
            check.constraint_name()

    def test_check_amount_positive_should_return_true(self):
        check = self.env['account.abstract.check'].new({'amount': 1})
        assert check._check_amount()

    def test_check_amount_zero_should_return_false(self):
        check = self.env['account.abstract.check'].new({'amount': 0})
        assert not check._check_amount()

    def test_check_amount_negative_should_return_false(self):
        check = self.env['account.abstract.check'].new({'amount': -1})
        assert not check._check_amount()

    def test_constraint_amount_zero_should_raise_error(self):
        check = self.env['account.abstract.check'].new({'amount': 0})
        with self.assertRaises(InvalidCheckAmountError):
            check.constraint_amount()

    def test_check_payment_issue_date_with_no_payment_date_should_return_true(self):
        check = self.env['account.abstract.check'].new({'payment_date': False})
        assert check._check_payment_issue_date()

    def test_check_payment_issue_date_with_payment_date_after_issue_date_should_return_true(self):
        today = fields.Date.today()
        day_delta = relativedelta(days=1)
        check = self.env['account.abstract.check'].new({'payment_date': today + day_delta, 'issue_date': today})
        assert check._check_payment_issue_date()

    def test_check_payment_issue_date_with_payment_date_same_as_issue_date_should_return_true(self):
        today = fields.Date.today()
        check = self.env['account.abstract.check'].new({'payment_date': today, 'issue_date': today})
        assert check._check_payment_issue_date()

    def test_check_payment_issue_date_with_payment_date_before_issue_date_should_return_false(self):
        today = fields.Date.today()
        day_delta = relativedelta(days=1)
        check = self.env['account.abstract.check'].new({'payment_date': today - day_delta, 'issue_date': today})
        assert not check._check_payment_issue_date()

    def test_check_payment_issue_date_in_common_check_with_not_common_check_should_return_true(self):
        check = self.env['account.abstract.check'].new({'check_type': 'postdated'})
        assert check._check_payment_issue_date_in_common_check()

    def test_check_payment_issue_date_in_common_check_with_payment_date_same_as_issue_date_should_return_true(self):
        today = fields.Date.today()
        check = self.env['account.abstract.check'].new({'check_type': 'common', 'payment_date': today, 'issue_date': today})
        assert check._check_payment_issue_date_in_common_check()

    def test_check_payment_issue_date_in_common_check_with_payment_date_after_issue_date_should_return_false(self):
        today = fields.Date.today()
        day_delta = relativedelta(days=1)
        check = self.env['account.abstract.check'].new({'check_type': 'common', 'payment_date': today + day_delta, 'issue_date': today})
        assert not check._check_payment_issue_date_in_common_check()

    def test_check_payment_issue_date_in_common_check_with_payment_date_before_issue_date_should_return_false(self):
        today = fields.Date.today()
        day_delta = relativedelta(days=1)
        check = self.env['account.abstract.check'].new({'check_type': 'common', 'payment_date': today - day_delta, 'issue_date': today})
        assert not check._check_payment_issue_date_in_common_check()

    def test_constraint_dates_with_payment_date_before_issue_date_should_raise_error(self):
        today = fields.Date.today()
        day_delta = relativedelta(days=1)
        check = self.env['account.abstract.check'].new({'payment_date': today - day_delta, 'issue_date': today})
        with self.assertRaises(InvalidCheckDatesError):
            check.constraint_dates()

    def test_constraint_dates_in_common_check_with_payment_date_after_issue_date_should_return_false(self):
        today = fields.Date.today()
        day_delta = relativedelta(days=1)
        check = self.env['account.abstract.check'].new({'check_type': 'common', 'payment_date': today + day_delta, 'issue_date': today})
        with self.assertRaises(NotEqualCheckDatesError):
            check.constraint_dates()

    def test_onchange_payment_type_with_not_common_check_should_not_change_payment_date(self):
        today = fields.Date.today()
        day_delta = relativedelta(days=1)
        check = self.env['account.abstract.check'].new({'check_type': 'postdated', 'payment_date': today + day_delta, 'issue_date': today})
        check.onchange_payment_type()
        assert check.payment_date == today + day_delta

    def test_onchange_payment_type_with_common_check_should_change_payment_date(self):
        today = fields.Date.today()
        day_delta = relativedelta(days=1)
        check = self.env['account.abstract.check'].new({'check_type': 'common', 'payment_date': today + day_delta, 'issue_date': today})
        check.onchange_payment_type()
        assert check.payment_date == today

    def test_check_state_for_cancel_payment_with_handed_check_should_return_true(self):
        check = self.env['account.abstract.check'].new({'state': 'handed'})
        assert check._check_state_for_cancel_payment()

    def test_check_state_for_cancel_payment_with_non_handed_check_should_return_false(self):
        check = self.env['account.abstract.check'].new({'state': 'draft'})
        assert not check._check_state_for_cancel_payment()

    def test_cancel_payment_with_non_handed_check_should_raise_error(self):
        check = self.env['account.abstract.check'].new({'state': 'draft'})
        with self.assertRaises(CancelPaymentNonHandedCheckError):
            check.cancel_payment()

    def test_cancel_payment_should_update_state(self):
        check = self.env['account.abstract.check'].new({'state': 'handed'})
        method = 'odoo.addons.l10n_account_check.models.account_abstract_check.AccountAbstractCheck.get_cancel_states'
        with mock.patch(method) as MockClass:
            MockClass.return_value = {'handed': 'draft'}
            check.cancel_payment()
        assert check.state == 'draft'

    def test_cancel_state_with_valid_transition_should_update_state(self):
        check = self.env['account.abstract.check'].new()
        method = 'odoo.addons.l10n_account_check.models.account_abstract_check.AccountAbstractCheck.get_cancel_states'
        with mock.patch(method) as MockClass:
            MockClass.return_value = {'example_draft': 'draft'}
            check.cancel_state('example_draft')
        assert check.state == 'draft'

    def test_cancel_state_with_invalid_transition_should_raise_error(self):
        check = self.env['account.abstract.check'].new()
        method = 'odoo.addons.l10n_account_check.models.account_abstract_check.AccountAbstractCheck.get_cancel_states'
        with mock.patch(method) as MockClass:
            MockClass.return_value = {}
            with self.assertRaises(InvalidCheckCancelStateError):
                check.cancel_state('example_draft')

    def test_next_state_with_valid_transition_should_update_state(self):
        check = self.env['account.abstract.check'].new()
        method = 'odoo.addons.l10n_account_check.models.account_abstract_check.AccountAbstractCheck.get_next_states'
        with mock.patch(method) as MockClass:
            MockClass.return_value = {'example_handed': 'handed'}
            check.next_state('example_handed')
        assert check.state == 'handed'

    def test_next_state_with_invalid_transition_should_raise_error(self):
        check = self.env['account.abstract.check'].new()
        method = 'odoo.addons.l10n_account_check.models.account_abstract_check.AccountAbstractCheck.get_next_states'
        with mock.patch(method) as MockClass:
            MockClass.return_value = {}
            with self.assertRaises(InvalidCheckNextStateError):
                check.next_state('example_draft')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
