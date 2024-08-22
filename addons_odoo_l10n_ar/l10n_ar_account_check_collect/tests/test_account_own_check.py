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
from odoo import fields
from odoo.exceptions import ValidationError


class TestAccountOwnCheck(common.TransactionCase):

    def setUp(self):
        super(TestAccountOwnCheck, self).setUp()
        own_check_proxy = self.env['account.own.check']
        date_today = fields.Date.context_today(own_check_proxy)
        journal_proxy = self.env['account.journal']
        self.check_journal_account = self.env.ref('l10n_ar.1_valores_diferidos_a_cobrar')
        self.check_journal = journal_proxy.create({
            'name': 'Cheques diferidos',
            'code': 'CHCK',
            'type': 'bank',
            'default_debit_account_id': self.check_journal_account.id,
            'default_credit_account_id': self.check_journal_account.id,

        })
        self.own_check = own_check_proxy.create({
            'name': '12345678',
            'journal_id': self.check_journal.id,
            'bank_id': self.env['res.bank'].search([], limit=1).id,
            'amount': 1750,
            'currency_id': self.env.company.currency_id.id,
            'issue_date': date_today,
            'payment_date': date_today,
            'state': 'draft',

        })

    def test_post_collect(self):
        # Cuando se cobra un pago deberian pasar los cheques a cobrado
        self.own_check.post_collect(None)
        assert self.own_check.state == 'collect'

    def test_post_collect_with_vals(self):
        own_check_proxy = self.env['account.own.check']
        date_today = fields.Date.context_today(own_check_proxy)
        vals = {
            'amount': 300,
            'payment_date': date_today,
            'issue_date': date_today,
            'collect_move_id': False, # Podria pasar un Mock
        }
        self.own_check.post_collect(vals)
        assert self.own_check.amount == 300
        assert self.own_check.state == 'collect'

    def test_cancel_collect(self):
        # Cuando se revierte un cobro deberian pasar los cheques a borrador
        self.own_check.post_collect(None)
        self.own_check.cancel_collect()
        assert self.own_check.state == 'draft'
        # No se deberia poder hacer esto si el cheque no esta en cobrado
        with self.assertRaises(ValidationError):
            self.own_check.cancel_collect()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
