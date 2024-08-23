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

from odoo import models, fields, api


class AccountThirdCheck(models.Model):
    _inherit = 'account.third.check'

    def get_wallet_report_end_date(self):
        if self.state == 'sold':
            return self.sold_date or self.sold_check_id.date
        if self.state == 'deposited':
            return self.deposit_date or self.deposit_slip_id.date
        if self.state == 'handed':
            return self.destination_payment_id.payment_date
        if self.state == 'rejected':
            return self.sold_date or self.sold_check_id.date or self.deposit_date or self.deposit_slip_id.date or \
                self.destination_payment_id.payment_date or self.reject_move_id.date or self.payment_date

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
