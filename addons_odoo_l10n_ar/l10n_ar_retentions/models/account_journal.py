# -*- encoding: utf-8 -*-

from odoo import models, fields


class AccountJournal(models.Model):

    _inherit = 'account.journal'

    payment_usage = fields.Selection(
        selection_add=[('retention', "Retención")]
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
