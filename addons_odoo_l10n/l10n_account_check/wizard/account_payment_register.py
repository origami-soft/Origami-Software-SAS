# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    # Cheques recibidos
    account_third_check_ids = fields.One2many(
        'register.account.third.check',
        'payment_id',
        'Cheques de terceros recibidos',
    )
    # Cheques entregados
    account_third_check_sent_ids = fields.Many2many(
        'account.third.check',
        string='Cheques de terceros entregados',
    )
    account_own_check_ids = fields.One2many(
        'register.account.own.check',
        'payment_id',
        'Cheques propios',
    )
    check_issue_date = fields.Date(compute='compute_check_issue_date')

    @api.onchange('account_third_check_ids', 'account_own_check_ids')
    def onchange_check_ids(self):
        self.recalculate_difference()

    @api.onchange('account_third_check_sent_ids')
    def onchange_third_checks_sent(self):
        for r in self.account_third_check_sent_ids.filtered(lambda c: not c.sent_rate):
            orig_check = r._origin
            rate = self.env['res.currency']._get_conversion_rate(
                self.currency_id, orig_check.currency_id, self.company_id, self.payment_date)
            r.sent_rate = rate
            r.onchange_sent_rate()
        self.recalculate_difference()

    @api.depends('payment_date')
    def compute_check_issue_date(self):
        for payment in self:
            payment.check_issue_date = payment.payment_date or fields.Date.today()

    def _create_payment_vals_from_wizard(self, batch_result):
        res = super()._create_payment_vals_from_wizard(batch_result)
        res['account_third_check_ids'] = [(0, 0, r.get_payment_line_vals()) for r in self.account_third_check_ids]
        res['account_own_check_ids'] = [(0, 0, r.get_payment_line_vals()) for r in self.account_own_check_ids]
        res['account_third_check_sent_ids'] = self.account_third_check_sent_ids
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
