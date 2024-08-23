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

from odoo import models, fields
from odoo.exceptions import ValidationError


class CheckWalletReportWizard(models.TransientModel):
    _name = 'check.wallet.report.wizard'

    date = fields.Date("Fecha", default=fields.Date.context_today)

    def get_check_domain(self):
        return [
            ('state', 'in', ('wallet', 'sold', 'deposited', 'handed', 'rejected')),
            ('payment_id.payment_date', '<=', self.date)
        ]

    def get_checks(self):
        return self.env['account.third.check'].search(self.get_check_domain()).filtered(
            lambda l: l.state == 'wallet' or l.get_wallet_report_end_date() and l.get_wallet_report_end_date() > self.date
        )
    
    def generate_report(self):
        checks = self.get_checks()
        if not checks:
            raise ValidationError("No se encontró ningún cheque que haya estado en cartera a esa fecha.")
        return {
            'name': f'Cheques en cartera al {self.date.strftime("%d/%m/%Y")}',
            'views': [[False, "tree"], [False, "form"]],
            'domain': [("id", 'in', checks.ids)],
            'res_model': 'account.third.check',
            'type': 'ir.actions.act_window',
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
