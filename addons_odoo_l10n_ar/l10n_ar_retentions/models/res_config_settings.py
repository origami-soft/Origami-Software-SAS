# -*- encoding: utf-8 -*-

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    account_payment_retention_journal_id = fields.Many2one(
        related='company_id.account_payment_retention_journal_id',
        string='Diario de retenciones',
        readonly=False,
        domain="[('company_id', '=', company_id), ('payment_usage', '=', 'retention')]"
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
