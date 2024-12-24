# -*- encoding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    account_third_check_journal_id = fields.Many2one(
        'account.journal',
        'Diario de cheques de terceros',
        domain="[('company_id', '=', id), ('payment_usage', '=', 'third_check')]"
    )
    account_own_check_journal_id = fields.Many2one(
        'account.journal',
        'Diario de cheques propios',
        domain="[('company_id', '=', id), ('payment_usage', '=', 'own_check')]"
    )
    own_check_bank_id = fields.Many2one(
        comodel_name='account.journal',
        string='Banco por defecto en cheques propios',
        domain="[('company_id', '=', company_id), ('type', '=', 'bank'), ('bank_id', '!=', False) ]"
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
