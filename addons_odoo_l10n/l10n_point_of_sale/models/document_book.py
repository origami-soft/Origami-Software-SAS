# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class DocumentBook(models.Model):
    _name = 'document.book'
    _description = 'Talonario'

    @api.depends('voucher_type_id.name', 'book_type_id.identifier')
    def _get_name(self):
        for book in self:
            book.name = "{voucher_name}{book_type_identifier}".format(voucher_name=book.voucher_type_id.name, book_type_identifier=" ({})".format(
                book.book_type_id.identifier) if book.book_type_id.identifier else '')

    name = fields.Char(
        string='Nombre', 
        compute='_get_name',
        store=True
    )
    pos_ar_id = fields.Many2one(
        comodel_name='pos.ar',
        string='Punto de venta',
        required=True,
        check_company=True
    )
    category = fields.Selection(
        selection=[('invoice', 'Factura'),
                   ('refund', 'Nota de crédito'),
                   ('payment_in', 'Cobro'),
                   ('payment_out', 'Pago'),
                   ('picking', 'Remito')],
        string='Categoria',
        required=True
    )
    book_type_id = fields.Many2one(
        comodel_name='document.book.type', 
        string='Tipo de talonario', 
        required=True
    )
    voucher_type_id = fields.Many2one(
        comodel_name='voucher.type',
        string='Tipo de comprobante',
        help="En los casos que se utilice el mismo punto de venta para distintos documentos\n"
             "Por ejemplo, facturas y notas de credito/debito"
    )
    active = fields.Boolean(
        string='Activo',
        default=True
    )
    sequence = fields.Integer(
        string='Secuencia', 
        help='Por default, se eligirá el que menos secuencia tiene'
    )
    company_id = fields.Many2one(related='pos_ar_id.company_id')

    _sql_constraints = [
        ('unique_document_book', 'unique (category, voucher_type_id, book_type_id, pos_ar_id)','El talonario debe ser unico por la combinacion punto de venta/tipo de talonario/categoria/tipo de comprobante')
    ]

    @api.onchange('category')
    def onchange_category(self):
        self.update({
            'book_type_id': None,
            'voucher_type_id': None,
        })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
