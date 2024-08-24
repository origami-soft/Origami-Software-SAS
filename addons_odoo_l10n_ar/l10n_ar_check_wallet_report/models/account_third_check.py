# -*- encoding: utf-8 -*-

from odoo import models


class AccountThirdCheck(models.Model):
    _inherit = 'account.third.check'

    def get_wallet_report_end_date(self):
        if self.state == 'sold':
            return self.sold_date or self.sold_check_id.date
        if self.state == 'deposited':
            return self.deposit_date or self.deposit_slip_id.date
        if self.state == 'handed':
            return self.destination_payment_id.date
        if self.state == 'rejected':
            return self.sold_date or self.sold_check_id.date or self.deposit_date or self.deposit_slip_id.date or \
                self.destination_payment_id.date or self.reject_move_id.date or self.reject_date

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
