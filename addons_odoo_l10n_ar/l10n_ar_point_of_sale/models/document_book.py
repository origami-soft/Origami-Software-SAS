# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class DocumentBook(models.Model):

    _inherit = 'document.book'

    last_number = fields.Char('Ultimo numero', size=8, copy=False)

    @api.constrains('last_number')
    def check_last_number(self):
        for document_book in self.filtered(lambda x: x.last_number):
            try:
                int(document_book.last_number)
            except Exception:
                raise ValidationError('El último número debe contener solo números enteros')

    def _next_number(self):
        """
        Suma uno al ultimo valor del talonario y lo devuelve
        :return: Numero para ser utilizado
        """
        self.last_number = int(self.last_number) + 1
        return self.get_number()

    def next_number(self):
        """
        Saltea permisos para ejecutar la funcion que avanza la numeracion
        :return: Numero para ser utilizado
        """
        return self.sudo()._next_number()

    def get_number(self):
        return self.sudo().last_number.zfill(8)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
