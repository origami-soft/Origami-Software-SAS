# -*- encoding: utf-8 -*-

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    credit_card_journal_id = fields.Many2one(
        related='company_id.credit_card_journal_id',
        string='Diario de tarjetas de crédito',
        readonly=False,
        domain="[('company_id', '=', company_id), ('payment_usage', '=', 'credit_card')]"
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
