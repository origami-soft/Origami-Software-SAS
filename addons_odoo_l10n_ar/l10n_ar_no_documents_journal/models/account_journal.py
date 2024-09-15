# -*- encoding: utf-8 -*-

from odoo import models, fields


class AccountJournal(models.Model):

    _inherit = 'account.journal'

    no_documents = fields.Boolean(
        string="NO Documents"
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
