# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PosAr(models.Model):

    _inherit = 'pos.ar'

    COPIES = {
        0: 'ORIGINAL',
        1: 'DUPLICADO',
        2: 'TRIPLICADO',
        3: 'CUADRUPLICADO'
    }

    copies_quantity = fields.Integer(
        string='Cantidad de copias',
        default=2,
    )

    def get_copie_name(self, key):
        """ Devuelvo el nombre de la copia del reporte """
        if self.COPIES.get(key):
            return self.COPIES[key]

    @api.constrains('copies_quantity')
    def check_quantity(self):
        """ Chequeo los valores de la cantidad de copias"""
        if self.copies_quantity < 1:
            raise ValidationError('La cantidad de copias no puede ser menor que 1.')
        if self.copies_quantity > 4:
            raise ValidationError('Si desea imprimir más de 4 copias por favor contáctese con el administrador.')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
