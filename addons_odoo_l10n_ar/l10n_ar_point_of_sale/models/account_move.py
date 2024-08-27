# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


class AccountMove(models.Model):

    _inherit = 'account.move'

    @api.model
    def _get_domain(self):
        country_id = self.env.ref('base.ar').id
        return [('country_id', '=', country_id)]

    pos_ar_id = fields.Many2one(
        'pos.ar',
        'Punto de venta',
        related='journal_id.pos_ar_id'
    )
    is_debit_note = fields.Boolean(
        'Es nota de debito?',
        related='voucher_type_id.is_debit_note'
    )
    is_credit_invoice = fields.Boolean(
        'Es factura de credito?',
        related='voucher_type_id.is_credit_invoice'
    )
    jurisdiction_id = fields.Many2one(
        comodel_name='res.country.state',
        string='Jurisdiccion',
        domain=_get_domain,
        ondelete='restrict'
    )
    voucher_name = fields.Char(
        'Numero documento',
        copy=False
    )
    available_voucher_type_ids = fields.Many2many(
        'voucher.type',
        compute='_compute_available_voucher_types'
    )
    voucher_type_id = fields.Many2one(
        'voucher.type',
        compute='_compute_voucher_type_id',
        readonly=False,
        store=True,
        ondelete='restrict',
        copy=True
    )

    # Dato que se va a utilizar desde diferentes modulos para poder aplicar
    # filtros y cambiar los datos que se visualizan en el formulario de una
    # factura. Ejemplo: En modulo de facturacion electronica solo se mostrara
    # cae y fecha vencimiento cae en caso de que el tipo de de talonario sea
    # electronico.
    document_book_type = fields.Char(
        compute='get_document_book_type',
        string='Tipo de talonario'
    )

    @api.constrains('name', 'journal_id', 'state')
    def _check_unique_sequence_number(self):
        """ Heredamos la función para que no incluya la validación estandar en un doc. de proveedor """
        purchase_invoices = self.filtered(lambda x: x.is_purchase_document())
        return super(AccountMove, self - purchase_invoices)._check_unique_sequence_number()

    @api.depends('fiscal_position_id', 'type')
    def _compute_available_voucher_types(self):
        self.available_voucher_type_ids = False
        for document in self.filtered(lambda x: x.fiscal_position_id):
            available_documents = document._get_available_documents()
            document.available_voucher_type_ids = available_documents

    @api.depends('fiscal_position_id', 'type')
    def _compute_voucher_type_id(self):
        for document in self:
            available_documents = document._get_available_documents()
            document.voucher_type_id = available_documents[0] if available_documents else None

    def _get_available_documents(self):
        """ Obtiene los posibles tipos de comprobantes a facturar en base a las posiciones fiscales """
        self.ensure_one()
        category = 'invoice' if self.type in ['in_invoice', 'out_invoice'] else \
            ('refund' if self.type in ['out_refund', 'in_refund'] else None)
        issue = self.fiscal_position_id if self.is_purchase_document() else self.company_id.account_position_id
        receipt = self.company_id.account_position_id if self.is_purchase_document() else self.fiscal_position_id
        available_documents = self.env['voucher.type'].get_available_documents(
            issue,
            receipt,
            category
        )
        return available_documents

    def check_invoice_duplicity(self):
        """ Valida que la factura no esté duplicada. """

        if self.is_invoice():
            domain = [
                ('voucher_name', 'ilike', self.voucher_name.lstrip("0")),
                ('voucher_type_id', '=', self.voucher_type_id.id),
                ('type', '=', self.type),
                ('state', 'not in', ['draft', 'cancel']),
                ('id', '!=', self.id),
                ('company_id', '=', self.company_id.id)
            ]
            if self.is_purchase_document():
                domain.append(('partner_id', '=', self.partner_id.id))
            
            duplicate_invoices = self.search(domain)
            
            # En caso de que la factura tenga un número de comprobante del estilo XXXX-XXXXXXXX, reviso entre las
            # facturas encontradas y descarto aquellas que tengan un número de punto de venta distinto (ya que el ilike
            # del search puede traer números que no corresponden)
            # Ej.: si mi factura tiene número 0001-00000001 y hay una con número 0011-00000001, la búsqueda de voucher
            # name va a ser ilike 1-00000001, por lo cual va a traer 0011-00000001 como "duplicada"
            if '-' in self.voucher_name and self.voucher_name.split('-')[0].isdigit():
                pos_number = int(self.voucher_name.split('-')[0])
                duplicate_invoices = duplicate_invoices.filtered(
                    lambda l: '-' in (l.voucher_name or '') and l.voucher_name.split('-')[0].isdigit() and int(l.voucher_name.split('-')[0]) == pos_number
                )

            if duplicate_invoices:
                raise ValidationError(
                    "Ya existe un documento del tipo {} con el número {}".format(
                        self.voucher_type_id.name,
                        self.voucher_name
                    )
                )

    def post(self):
        for invoice in self.filtered(lambda x: x.voucher_type_id):
            if not invoice.amount_total:
                raise ValidationError('No pueden validarse documentos con monto total igual a cero.')

            # Obtenemos el proximo numero o validamos su estructura
            if not invoice.is_purchase_document() and invoice.pos_ar_id:
                document_book = invoice.validate_document_book()
                # Llamamos a la funcion a ejecutarse desde el tipo de talonario,
                # de esta forma, hará lo correspondiente
                # para distintos casos (preimpreso, electronica, fiscal, etc.)
                getattr(invoice, document_book.book_type_id.foo)(document_book)

            elif invoice.is_purchase_document():
                invoice._validate_supplier_invoice_number()
            
            if invoice.is_sale_document() and invoice.voucher_type_id and not invoice.pos_ar_id:
                raise ValidationError("El diario {} sobre el que intenta facturar no posee punto de venta.".format(invoice.journal_id.name))

            invoice.set_voucher_name()
            invoice.check_invoice_duplicity()
        for invoice in self.filtered(lambda x: not x.voucher_type_id and x.type in ['in_invoice', 'in_refund']):
            invoice.set_in_voucher_name()
        return super(AccountMove, self).post()

    def set_in_voucher_name(self):
        """ Asigna el nombre del documento segun el nombre del documento"""
        self.ensure_one()
        self.name = '{}'.format(
            self.voucher_name
        )

    def set_voucher_name(self):
        """ Asigna el nombre del documento segun el tipo de documento y el punto de venta """
        self.ensure_one()
        if not self.voucher_name and self.pos_ar_id:
            self.voucher_name = '{}-{}'.format(
                self.pos_ar_id.name.zfill(self.pos_ar_id.prefix_quantity or 0),
                self.pos_ar_id.next_number(self.voucher_type_id)
            )
        self.name = '{}{}'.format(
            self.voucher_type_id.prefix + ' ' if self.voucher_type_id.prefix else '',
            self.voucher_name or ''
        )

    def validate_document_book(self):
        self.ensure_one()
        if not self.voucher_type_id:
            raise ValidationError("Por favor, asignar tipo de comprobante")
        document_book = self.get_document_book()
        if not document_book:
            raise ValidationError(
                'No existe talonario configurado para el punto de venta {} y el tipo de comprobante {}'.format(
                    self.pos_ar_id.name_get()[0][1], self.voucher_type_id.name
                ))
        return document_book

    def get_document_book(self):
        """
        Busca el talonario obtenido del punto de venta y tipo de comprobante.
        :return: Talonario a utilizar
        """
        self.ensure_one()
        document_book = self.env['document.book']
        if self.voucher_type_id and self.pos_ar_id:
            domain = [
                ('voucher_type_id', '=', self.voucher_type_id.id),
                ('pos_ar_id', '=', self.pos_ar_id.id),
            ]
            document_book = document_book.search(domain, limit=1)
        return document_book

    @api.depends('voucher_type_id', 'pos_ar_id')
    def get_document_book_type(self):
        for inv in self:
            inv.document_book_type = inv.get_document_book().book_type_id.type

    def action_preprint(self, document_book):
        """ Funcion para ejecutarse al validar una factura con talonario preimpreso """
        return

    @api.depends('voucher_type_id', 'pos_ar_id')
    def compute_document_book_type(self):
        for inv in self:
            book_type = inv.get_document_book().book_type_id.type if inv.voucher_type_id and inv.pos_ar_id else None
            inv.document_book_type = book_type

    def _validate_supplier_invoice_number(self):
        """
        Validamos el numero de factura
        :raise ValidationError: Si no cumple con el formato xxxx-xxxxxxxx, y debe tener solo enteros
        """

        if not self.voucher_name:
            raise ValidationError('El documento no tiene numero!')

        if self.voucher_type_id.denomination_id.validate_supplier:
            invoice_number = self.voucher_name.split('-')
            error_msg = "Formato invalido, el documento debe tener el formato 'xxxxx-xxxxxxxx' y contener solo números!"

            # Nos aseguramos que contenga '-' para separar punto de venta de numero
            if len(invoice_number) != 2:
                raise ValidationError(error_msg)

            # Rellenamos con 0s los valores necesarios
            point_of_sale = invoice_number[0].zfill(4)
            number = invoice_number[1].zfill(8)
            invoice_number = point_of_sale+'-'+number

            # Validamos el formato y se lo ponemos a la factura
            if not re.match('^([0-9]{4}|[0-9]{5})-[0-9]{8}$', invoice_number):
                raise ValidationError(error_msg)

            self.voucher_name = invoice_number

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
