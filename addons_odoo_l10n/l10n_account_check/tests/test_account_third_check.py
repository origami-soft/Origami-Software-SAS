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
from ..exceptions.exceptions import CheckInOtherPaymentError, DeleteNonDraftCheckError, PostReceiptNonDraftCheckError,\
    PostPaymentNonWalletCheckError, PostPaymentNotToOrderCheckError, CancelReceiptNonWalletCheckError


class TestAccountThirdCheck(TransactionCase):

    def setUp(self):
        super(TestAccountThirdCheck, self).setUp()

    def test_check_linked_payments_with_no_payments_should_return_true(self):
        check = self.env['account.third.check'].new({'account_payment_ids': False})
        assert check._check_linked_payments()

    def test_check_linked_payments_with_one_payment_should_return_true(self):
        payment = self.env['account.payment'].new()
        check = self.env['account.third.check'].new({'account_payment_ids': payment})
        assert check._check_linked_payments()

    def test_check_linked_payments_with_two_payments_should_return_false(self):
        payment_one = self.env['account.payment'].new()
        payment_two = self.env['account.payment'].new()
        check = self.env['account.third.check'].new({'account_payment_ids': payment_one | payment_two})
        assert not check._check_linked_payments()

    def test_constraint_payments_with_two_payments_should_raise_error(self):
        payment_one = self.env['account.payment'].new()
        payment_two = self.env['account.payment'].new()
        check = self.env['account.third.check'].new({'account_payment_ids': payment_one | payment_two})
        with self.assertRaises(CheckInOtherPaymentError):
            check.constraint_payments()

    def test_check_unlink_state_with_draft_check_should_return_true(self):
        check = self.env['account.third.check'].new({'state': 'draft'})
        assert check._check_unlink_state()

    def test_check_unlink_state_with_non_draft_check_should_return_false(self):
        check = self.env['account.third.check'].new({'state': 'deposited'})
        assert not check._check_unlink_state()

    def test_unlink_with_non_draft_check_should_raise_error(self):
        check = self.env['account.third.check'].new({'state': 'deposited'})
        with self.assertRaises(DeleteNonDraftCheckError):
            check.unlink()

    def test_check_post_receipt_state_with_draft_check_should_return_true(self):
        check = self.env['account.third.check'].new({'state': 'draft'})
        assert check._check_post_receipt_state()

    def test_check_post_receipt_state_with_non_draft_check_should_return_false(self):
        check = self.env['account.third.check'].new({'state': 'deposited'})
        assert not check._check_post_receipt_state()

    def test_post_receipt_with_non_draft_check_should_raise_error(self):
        check = self.env['account.third.check'].new({'state': 'deposited'})
        with self.assertRaises(PostReceiptNonDraftCheckError):
            check.post_receipt(self.env.company.currency_id)

    def test_post_receipt_with_currency_should_set_currency_and_state(self):
        usd = self.env.ref('base.USD')
        check = self.env['account.third.check'].new({'state': 'draft'})
        check.post_receipt(usd)
        assert check.currency_id == usd
        assert check.state == 'wallet'

    def test_check_post_payment_state_with_wallet_check_should_return_true(self):
        check = self.env['account.third.check'].new({'state': 'wallet'})
        assert check._check_post_payment_state()

    def test_check_post_payment_state_with_non_wallet_check_should_return_false(self):
        check = self.env['account.third.check'].new({'state': 'deposited'})
        assert not check._check_post_payment_state()

    def test_post_payment_with_non_wallet_check_should_raise_error(self):
        check = self.env['account.third.check'].new({'state': 'deposited'})
        with self.assertRaises(PostPaymentNonWalletCheckError):
            check.post_payment()

    def test_post_payment_with_not_to_order_check_should_raise_error(self):
        check = self.env['account.third.check'].new({'state': 'wallet', 'not_to_order': True})
        with self.assertRaises(PostPaymentNotToOrderCheckError):
            check.post_payment()

    def test_post_payment_should_set_state(self):
        check = self.env['account.third.check'].new({'state': 'wallet'})
        check.post_payment()
        assert check.state == 'handed'

    def test_check_cancel_receipt_state_with_wallet_check_should_return_true(self):
        check = self.env['account.third.check'].new({'state': 'wallet'})
        assert check._check_cancel_receipt_state()

    def test_check_cancel_receipt_state_with_non_wallet_check_should_return_false(self):
        check = self.env['account.third.check'].new({'state': 'deposited'})
        assert not check._check_cancel_receipt_state()

    def test_cancel_receipt_with_non_wallet_check_should_raise_error(self):
        check = self.env['account.third.check'].new({'state': 'deposited'})
        with self.assertRaises(CancelReceiptNonWalletCheckError):
            check.cancel_receipt()

    def test_cancel_receipt_should_set_state(self):
        check = self.env['account.third.check'].new({'state': 'wallet'})
        check.cancel_receipt()
        assert check.state == 'draft'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
