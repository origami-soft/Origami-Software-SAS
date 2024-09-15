# -*- encoding: utf-8 -*-

from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    deposit_slip_id = fields.Many2one(
        'account.deposit.slip',
        'Boleta de depósito',
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
