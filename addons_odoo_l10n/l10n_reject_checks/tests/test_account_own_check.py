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

from odoo.tests import common
from odoo.exceptions import ValidationError


class TestAccountOwnCheck(common.TransactionCase):

    def setUp(self):
        super(TestAccountOwnCheck, self).setUp()
        own_check_proxy = self.env['account.own.check']
        bank = self.env['res.bank'].new()
        journal = self.env['account.journal'].new({'bank_id': bank, 'bank_acc_number': 'Banco 1231'})
        self.own_check_draft = own_check_proxy.new({
            'name': '12345678',
            'bank_id': bank,
            'check_type': 'common',
            'state': 'draft'
        })
        self.own_check_handed = own_check_proxy.new({
            'name': '12345678',
            'bank_id': bank,
            'check_type': 'common',
            'state': 'handed'
        })
        self.own_checks = self.own_check_draft | self.own_check_handed

    def test_cancel_check(self):
        self.own_check_handed.state = 'draft'
        self.own_checks.cancel_check()
        assert all(check == 'canceled' for check in self.own_checks.mapped("state"))

    def test_invalid_cancel_check(self):
        with self.assertRaises(ValidationError):
            self.own_checks.cancel_check()

    def test_revert_canceled_check(self):
        self.own_checks.write({'state': 'canceled'})
        self.own_checks.revert_canceled_check()
        assert all(check == 'draft' for check in self.own_checks.mapped("state"))

    def test_invalid_revert_canceled_check(self):
        with self.assertRaises(ValidationError):
            self.own_checks.revert_canceled_check()

    def test_reject_check(self):
        self.own_check_draft.state = 'handed'
        self.own_checks.reject_check()
        assert all(check == 'rejected' for check in self.own_checks.mapped("state"))

    def test_invalid_reject_check(self):
        with self.assertRaises(ValidationError):
            self.own_checks.reject_check()

    def test_revert_reject(self):
        self.own_checks.write({'state': 'rejected'})
        self.own_checks.revert_reject()
        assert all(check == 'handed' for check in self.own_checks.mapped("state"))

    def test_invalid_revert_reject(self):
        with self.assertRaises(ValidationError):
            self.own_checks.revert_reject()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
