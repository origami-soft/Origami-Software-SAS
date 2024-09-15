# -*- encoding: utf-8 -*-

from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    account_abstract_line_id = fields.Many2one('account.abstract.payment.line', string="Modelo abstracto de líneas", default=False)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
