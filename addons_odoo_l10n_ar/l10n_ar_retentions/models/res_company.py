# -*- encoding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):

    _inherit = 'res.company'

    account_payment_retention_journal_id = fields.Many2one(
        'account.journal',
        'Diario por default para retenciones',
        domain="[('company_id', '=', id), ('payment_usage', '=', 'retention')]"
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
