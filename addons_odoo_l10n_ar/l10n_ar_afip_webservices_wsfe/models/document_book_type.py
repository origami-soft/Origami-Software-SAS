# -*- encoding: utf-8 -*-

from odoo import models, fields


class DocumentBookType(models.Model):

    _inherit = 'document.book.type'

    type = fields.Selection(
        selection_add=[
            ('electronic', 'Electronico'),
            ('electronic_exportation', 'Electronico exp.'),
            ('fiscal_electronic_bond', 'Bono Fiscal Electrónico')
        ],
        ondelete={
            'electronic': lambda recs: recs.write({'type': 'preprint'}),
            'electronic_exportation': lambda recs: recs.write({'type': 'preprint'}),
            'fiscal_electronic_bond': lambda recs: recs.write({'type': 'preprint'}),
        }
    )

    def get_electronic_types(self):
        return ['electronic', 'electronic_exportation', 'fiscal_electronic_bond']

    def is_electronic(self):
        if not self:
            return False
        electronic_types = self.get_electronic_types()
        return all(l.type in electronic_types for l in self)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
