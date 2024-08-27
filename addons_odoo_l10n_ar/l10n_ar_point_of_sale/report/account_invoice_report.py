# -*- encoding: utf-8 -*-

from odoo import models, fields


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    jurisdiction_id = fields.Many2one('res.country.state', 'Jurisdicción', readonly=True)

    def _select(self):
        return super(AccountInvoiceReport, self)._select() + ", move.jurisdiction_id"

    def _group_by(self):
        return super(AccountInvoiceReport, self)._group_by() + ", move.jurisdiction_id"

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
