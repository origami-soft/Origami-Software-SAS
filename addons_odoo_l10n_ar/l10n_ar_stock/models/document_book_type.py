# -*- encoding: utf-8 -*-

from odoo import models, fields


class DocumentBookType(models.Model):
    _inherit = 'document.book.type'

    type = fields.Selection(
        selection_add=[('selfprint', 'Autoimpresor')],
        ondelete={'selfprint': lambda recs: recs.write({'type': 'preprint'})}
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
