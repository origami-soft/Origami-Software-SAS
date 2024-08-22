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


class TestAccountJournal(TransactionCase):
    def test_onchange_type_with_bank_type_and_multiple_payment_should_keep_multiple_payment(self):
        journal = self.env['account.journal'].new({'type': 'bank', 'multiple_payment_journal': True})
        journal.onchange_type_set_multiple_payment_journal()
        assert journal.multiple_payment_journal

    def test_onchange_type_with_cash_type_and_multiple_payment_should_keep_multiple_payment(self):
        journal = self.env['account.journal'].new({'type': 'cash', 'multiple_payment_journal': True})
        journal.onchange_type_set_multiple_payment_journal()
        assert journal.multiple_payment_journal

    def test_onchange_type_with_other_type_and_multiple_payment_should_set_multiple_payment_to_false(self):
        journal = self.env['account.journal'].new({'multiple_payment_journal': True})
        journal.onchange_type_set_multiple_payment_journal()
        assert not journal.multiple_payment_journal

    def test_onchange_type_with_bank_type_and_no_multiple_payment_should_keep_no_multiple_payment(self):
        journal = self.env['account.journal'].new({'type': 'bank', 'multiple_payment_journal': False})
        journal.onchange_type_set_multiple_payment_journal()
        assert not journal.multiple_payment_journal

    def test_onchange_type_with_cash_type_and_no_multiple_payment_should_keep_no_multiple_payment(self):
        journal = self.env['account.journal'].new({'type': 'cash', 'multiple_payment_journal': False})
        journal.onchange_type_set_multiple_payment_journal()
        assert not journal.multiple_payment_journal

    def test_onchange_type_with_other_type_and_no_multiple_payment_should_set_multiple_payment_to_false(self):
        journal = self.env['account.journal'].new({'multiple_payment_journal': False})
        journal.onchange_type_set_multiple_payment_journal()
        assert not journal.multiple_payment_journal

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
