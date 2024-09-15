# -*- encoding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):

    _inherit = 'res.company'

    credit_card_journal_id = fields.Many2one(
        'account.journal',
        'Diario por default de tarjetas de crédito',
        domain="[('company_id', '=', id), ('payment_usage', '=', 'credit_card')]"
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
