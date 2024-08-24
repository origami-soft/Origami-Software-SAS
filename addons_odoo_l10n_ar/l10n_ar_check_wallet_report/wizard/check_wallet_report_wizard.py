# -*- encoding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import ValidationError


class CheckWalletReportWizard(models.TransientModel):
    _name = 'check.wallet.report.wizard'

    date = fields.Date("Fecha", default=fields.Date.context_today)

    def get_check_domain(self):
        return [
            ('state', 'in', ('wallet', 'sold', 'deposited', 'handed', 'rejected')),
            ('payment_id.date', '<=', self.date)
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
