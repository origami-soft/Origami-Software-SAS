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

from . import test_account_own_check
from odoo import fields


class TestAccountCheckCollectWizard(test_account_own_check.TestAccountOwnCheck):

    def setUp(self):
        super(TestAccountCheckCollectWizard, self).setUp()
        collect_wizard_proxy = self.env['account.check.collect.wizard']
        self.collect_wizard = collect_wizard_proxy.create({
            'amount': 200.0,
            'account_id': self.env['account.account'].search([], limit=1).id,
            'journal_id': self.env['account.journal'].search([], limit=1).id,
            'payment_date': fields.Date.context_today(collect_wizard_proxy),
            'collect_date': fields.Date.context_today(collect_wizard_proxy),
            'issue_date': fields.Date.context_today(collect_wizard_proxy),
            'name': '12345679',
            'check_type': 'postdated',
            'check_journal_id': self.check_journal.id,
            'bank_id': self.env['res.bank'].search([], limit=1).id,
        })

    def test_collect_check(self):
        own_check = self.collect_wizard._create_collect_check()
        ref = 'Cobro de cheque {check}'.format(
            check=own_check.name_get()[0][1]
        )
        move = self._create_collect_move(own_check, ref)
        move.post()
        assert own_check.amount == 200.0
        own_check.post_collect({'collect_move_id': move.id})
        assert own_check.state == 'collect'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
