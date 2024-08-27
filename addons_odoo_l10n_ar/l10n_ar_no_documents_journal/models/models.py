# -*- coding: utf-8 -*-
from odoo import http, models, fields, api, _
from datetime import datetime
import calendar

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    no_documents = fields.Boolean(string="NO Documents",translate=True,index=True)

class InvoiceAfipPresentation(models.AbstractModel):
    _inherit = 'invoice.afip.presentation'

    def get_domain_invoices(self):
        res = super(InvoiceAfipPresentation, self).get_domain_invoices()
        res.append(('journal_id.no_documents', '=', False))
        return res
