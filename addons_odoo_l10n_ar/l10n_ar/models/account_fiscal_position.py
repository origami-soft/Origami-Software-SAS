# -*- encoding: utf-8 -*-

from odoo import models, fields


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    ar_fiscal_position_id = fields.Many2one(
        comodel_name='ar.fiscal.position',
        string='Posición fiscal (AR)',
        ondelete='set null'
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
