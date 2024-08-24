# -*- encoding: utf-8 -*-

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    account_third_check_journal_id = fields.Many2one(
        related='company_id.account_third_check_journal_id',
        string='Diario de cheques de terceros',
        readonly=False,
        domain="[('company_id', '=', company_id), ('payment_usage', '=', 'third_check')]"
    )
    account_own_check_journal_id = fields.Many2one(
        related='company_id.account_own_check_journal_id',
        string='Diario de cheques propios',
        readonly=False,
        domain="[('company_id', '=', company_id), ('payment_usage', '=', 'own_check') ]"
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
