# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class DocumentBookType(models.Model):
    _name = 'document.book.type'
    _description = 'Tipo de talonario'

    def _get_name(self):
        for book in self:
            # Obtenemos el valor del nombre del campo seleccion para la categoria
            selection_value = dict(book.fields_get()['type']['selection'])[book.type]
            book.name = selection_value

    name = fields.Char(
        string='Nombre', 
        compute='_get_name'
    )
    identifier = fields.Char(
        string="Identificador",
        help="Identificador del tipo de talonario para mostrar en el nombre del talonario"
    )
    type = fields.Selection(
        selection=[('preprint', 'Preimpreso')], 
        string='Tipo', 
        required=True
    )
    category = fields.Selection(
        selection=[('invoice', 'Factura'),
        ('refund', 'Nota de crédito'),
        ('payment_out', 'Pago'),
        ('payment_in', 'Cobro'),
        ('picking', 'Remito')],
        string='Categoria',
    )
    foo = fields.Char(
        string='Funcion', 
        help='Funcion a ejecutarse al utilizar tipo de talonario'
    )
    use_automatic_sequence = fields.Boolean(
        string='Usa secuencia automática',
        help="Los comprobantes que usen este tipo de talonario se considerarán para calcular una secuencia automática",
        default=False
    )
    active = fields.Boolean(default=False)

    # _sql_constraints = [(
    #     'unique_type_categ',
    #     'unique(type, category)',
    #     'Ya existe ese tipo de talonario para esa categoría'
    # )]

    @api.model
    def unlink(self):
        for record in self:
            record.active = False
        return True
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
