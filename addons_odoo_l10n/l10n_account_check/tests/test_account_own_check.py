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
from ..exceptions.exceptions import PostPaymentNonDraftCheckError


class TestAccountOwnCheck(TransactionCase):

    def setUp(self):
        super(TestAccountOwnCheck, self).setUp()

    def test_check_post_payment_state_with_draft_check_should_return_true(self):
        check = self.env['account.own.check'].new({'state': 'draft'})
        assert check._check_post_payment_state()

    def test_check_post_payment_state_with_non_draft_check_should_return_false(self):
        check = self.env['account.own.check'].new({'state': 'canceled'})
        assert not check._check_post_payment_state()

    def test_post_payment_with_non_draft_check_should_raise_error(self):
        check = self.env['account.own.check'].new({'state': 'canceled'})
        with self.assertRaises(PostPaymentNonDraftCheckError):
            check.post_payment({})

    def test_post_payment_should_set_state_and_update_from_vals(self):
        payment = self.env['account.payment'].new({})
        check = self.env['account.own.check'].new({'state': 'draft'})
        check.post_payment({'destination_payment_id': payment})
        assert check.state == 'handed'
        assert check.destination_payment_id == payment

    def test_cancel_payment_should_clear_destination_payment(self):
        payment = self.env['account.payment'].new({})
        check = self.env['account.own.check'].new({'state': 'handed', 'destination_payment_id': payment})
        check.cancel_payment()
        assert not check.destination_payment_id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
