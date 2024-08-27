# -*- encoding: utf-8 -*-

from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    reconciled_check_id = fields.Many2one(
        comodel_name='account.own.check',
        string="Cheque debitado",
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
