# -*- encoding: utf-8 -*-

from odoo import models


class PosAr(models.Model):

    _inherit = 'pos.ar'

    def set_last_number_of_document_books(self):
        pos = self.browse(self.env.context.get('active_id'))
        for document_book in pos.document_book_ids:
            document_book.set_last_number_of_book_from_afip()
            self.env.cr.commit()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
