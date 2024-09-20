# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


class AccountMove(models.Model):

    _inherit = 'account.move'

    @api.model
    def _get_domain(self):
        country_id = self.env.ref('base.ar').id
        return [('country_id', '=', country_id)]

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

    @api.depends("pos_ar_id", "move_type", "partner_id")  # Se agrega dependencia de partner_id
    def compute_document_book(self):
        return super().compute_document_book()

    @api.depends("pos_ar_id", "move_type", "partner_id")  # Se agrega dependencia de partner_id
    def compute_pos_document_book_ids(self):
        return super().compute_pos_document_book_ids()
    
    @api.depends('voucher_name', 'voucher_type_id', 'voucher_type_id.prefix')
    def compute_full_voucher_name(self):
        for r in self:
            if r.voucher_type_id and r.voucher_name:
                r.full_voucher_name = f"{r.voucher_type_id.prefix} {r.voucher_name}"
            elif r.voucher_name:
                r.full_voucher_name = r.voucher_name
            else:
                r.full_voucher_name = r.name

    def action_post(self):
        """ Verifica que si la factura se va a enviar al Organismo correspondiente tenga talonario si es necesario

            :raise ValidationError: si falta el talonario en la factura
        """
        for rec in self.filtered(lambda x: x.move_type in ['out_invoice', 'out_refund']
                                           and x.pos_ar_id and not x.document_book_id):
            raise ValidationError('La factura no tiene talonario asignado.')

        return super().action_post()

    def get_params_for_available_vouchers_ar(self, params):
        """Método de la localización Argentina para filtrar
        talonarios y tipos de comprobante según la denominación

        :param params: Diccionario con parámetros genéricos
        :type params: dict()
        :return: Diccionario con los parámetros de la localización Argentina
        :rtype: dict()
        """
        return self._get_document_books_ar(params)

    def get_params_for_document_books_ar(self, params):
        """
        Método de la localización Argentina para filtrar
        los tipos de comprobante según la denominación y tipo de factura

        :param params: Diccionario con parámetros genéricos
        :type params: dict()
        :return: Diccionario con los parámetros de la localización Argentina
        :rtype: dict()
        """
        return self._get_document_books_ar(params)

    def _get_document_books_ar(self, params):
        issue = self.fiscal_position_id if self.is_purchase_document() else self.company_id.account_position_id
        receipt = self.company_id.account_position_id if self.is_purchase_document() else self.fiscal_position_id
        denominations = issue.get_available_denominations(receipt)
        if self.env.context.get('refund'):
            params['denomination_ids'] = [self.voucher_type_id.denomination_id.id]
        else:
            params['denomination_ids'] = denominations.ids
        return params

    @api.depends('journal_id', 'date')
    def _compute_highest_name(self):
        purchase_invoices = self.filtered(lambda x: x.is_purchase_document())
        purchase_invoices.highest_name = ''
        super(AccountMove, self - purchase_invoices)._compute_highest_name()

    def get_voucher_type_id(self):
        super(AccountMove, self).get_voucher_type_id()
        docs = self._get_available_documents()
        return docs and docs[0] or False

    def _get_available_documents(self):
        """ Obtiene los posibles tipos de comprobantes a facturar en base a las posiciones fiscales """
        self.ensure_one()
        category = 'invoice' if self.move_type in ['in_invoice', 'out_invoice'] else \
            ('refund' if self.move_type in ['out_refund', 'in_refund'] else None)
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
        if self.is_invoice() and self.voucher_name:
            domain = [
                ('voucher_name', 'ilike', self.voucher_name.lstrip("0")),
                ('voucher_type_id', '=', self.voucher_type_id.id),
                ('move_type', '=', self.move_type),
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

    def _post(self, soft=False):
        res = super(AccountMove, self)._post(soft)
        for invoice in self.filtered(lambda x: x.voucher_type_id):
            if not invoice.amount_total:
                raise ValidationError('No pueden validarse documentos con monto total igual a cero.')

            if invoice.is_purchase_document():
                invoice._validate_supplier_invoice_number()
                invoice.set_voucher_name()

            invoice.check_invoice_duplicity()
            invoice.set_line_name_on_voucher_name()
        return res

    def action_preprint(self):
        self.set_voucher_name()

    def set_voucher_name(self):
        self.ensure_one()
        if not self.voucher_name and self.pos_ar_id:
            self.voucher_name = '{}-{}'.format(
                self.pos_ar_id.name.zfill(self.pos_ar_id.prefix_quantity or 0),
                self.pos_ar_id.next_number(self.voucher_type_id)
            )
    
    def set_line_name_on_voucher_name(self):
        self.line_ids.filtered(lambda l: l.account_id.account_type in ('asset_receivable', 'liability_payable'))\
            .with_context(skip_invoice_integrity_check=True).write({'name': self.full_voucher_name})

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
