# -*- encoding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import ValidationError


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    def validate_cai_fields(self, document_book):
        self.ensure_one()
        if document_book.book_type_id.type != 'selfprint':
            raise ValidationError("No se puede asignar CAI en base a talonarios no autoimpresores")

        if not document_book.cai:
            raise ValidationError("El talonario no posee CAI")

        if document_book.cai_due_date < fields.Date.today():
            raise ValidationError("El CAI del talonario se encuentra vencido")

        number = int(document_book.last_number)
        if number >= document_book.cai_max_number:
            raise ValidationError("El número del talonario se encuentra por fuera de los límites definidos en el mismo")

        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
