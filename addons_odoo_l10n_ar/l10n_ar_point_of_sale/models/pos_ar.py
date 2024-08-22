# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PosAr(models.Model):
    _inherit = 'pos.ar'
    _description = 'Punto de venta'

    prefix_quantity = fields.Integer(
        'Cantidad de dígitos prefijo',
        default=4
    )

    def compare_name(self, other_pos):
        """ Piso el método original para contemplar los dígitos de prefijo (así, por ejemplo, no se permite crear un
        punto de venta "1" y otro "0001")
        """
        return self.name.zfill(self.prefix_quantity) == other_pos.name.zfill(other_pos.prefix_quantity)

    @api.constrains('name')
    def check_name(self):
        for pos_ar in self.filtered(lambda x: x.company_id.country_id == self.env.ref('base.ar')):
            try:
                int(pos_ar.name)
            except Exception:
                raise ValidationError('El nombre debe contener solo números enteros')
            if len(pos_ar.name) > pos_ar.prefix_quantity:
                raise ValidationError("No puede haber más dígitos que lo establecidos en la cantidad.")

    @api.constrains('prefix_quantity')
    def prefix_quantity_constraint(self):
        if any(pos.prefix_quantity <= 0 for pos in self):
            raise ValidationError("La cantidad de dígitos del prefijo debe ser mayor que 0")

    def next_number(self, voucher_type):
        self.ensure_one()
        document_book = self.document_book_ids.filtered(lambda x: x.voucher_type_id == voucher_type)
        if len(document_book) != 1:
            raise ValidationError(
                "No se encontro talonario para el punto de venta {} y el tipo de documento {}".format(
                    self.name, voucher_type.name
                )
            )
        return document_book.next_number()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
