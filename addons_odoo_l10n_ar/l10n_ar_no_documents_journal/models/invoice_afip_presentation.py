# -*- encoding: utf-8 -*-

from odoo import models


class InvoiceAfipPresentation(models.AbstractModel):
    _inherit = 'invoice.afip.presentation'

    def get_domain_invoices(self):
        res = super(InvoiceAfipPresentation, self).get_domain_invoices()
        res.append(('journal_id.no_documents', '=', False))
        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
