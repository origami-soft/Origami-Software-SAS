# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.misc import ustr
from odoo.exceptions import ValidationError

BOOK_TYPE_CATEGORIES = {
    'out_invoice': 'invoice',
    'out_refund': 'refund'
}

# Cada localización debe adoptar un nombre de método que sea el 
# de la variable a continuación más el código de país (en minúscula)
# para agregar las denominaciones correspondientes al filtro de comprobantes
# y para determinar el nombre del comprobante
DEFAULT_DOCUMENT_BOOK_FUNC = 'get_params_for_available_vouchers_'
AVAILABLE_DOCUMENT_BOOK_FUNC = 'get_params_for_document_books_'
FULL_VOUCHER_NAME_FUNC = 'get_full_voucher_name_'


class AccountMove(models.Model):
    _inherit = 'account.move'

    pos_ar_id = fields.Many2one(
        comodel_name='pos.ar',
        string='Punto de venta',
        related='journal_id.pos_ar_id'
    )
    document_book_id = fields.Many2one(
        comodel_name='document.book',
        string='Talonario',
        compute='compute_document_book',
        readonly=False,
        store=True,
        check_company=True,
        ondelete='restrict'
    )
    # Dato que se va a utilizar desde diferentes modulos para poder aplicar
    # filtros y cambiar los datos que se visualizan en el formulario de una
    # factura. Ejemplo: En modulo de facturacion electronica solo se mostrara
    # cae y fecha vencimiento cae en caso de que el tipo de de talonario sea
    # electronico.
    document_book_type = fields.Selection(
        related='document_book_id.book_type_id.type',
        string='Tipo de talonario'
    )
    # Dato para filtrar los talonarios a elegir según el punto de venta y la categoria
    pos_document_book_ids = fields.Many2many(
        comodel_name='document.book',
        compute="compute_pos_document_book_ids"
    )
    full_voucher_name = fields.Char(
        "Número completo",
        compute='compute_full_voucher_name',
        store=True,
    )

    def _get_fields_to_skip(self):
        return ['name', 'date']

    def _get_integrity_hash_fields(self):
        res = super()._get_integrity_hash_fields()
        if self._context.get('skip_invoice_integrity_check'):
            return [x for x in res if x not in self._get_fields_to_skip()]
        return res

    def _get_invoice_report_filename(self, extension='pdf'):
        """ Piso el método para que el nombre del archivo sea en base a full_voucher_name en vez de name """
        self.ensure_one()
        return f"{self.full_voucher_name.replace('/', '_')}.{extension}"

    def _get_full_voucher_name_depends_fields(self):
        """Cada localización agregará a este método los campos
        que requiera para calcular el full_voucher_name
        """
        return ['name']

    def _get_full_voucher_name(self, full_voucher_name_func):
        self.ensure_one()
        country = self.company_id.country_id
        if not country:
            return self.name
        country_code = country.code.lower()
        if not ustr(country_code).encode('utf-8').isalpha():
            return self.name
        func = getattr(self, full_voucher_name_func + country_code, None)
        if not func:
            return self.name
        return func()

    @api.depends(lambda self: self._get_full_voucher_name_depends_fields())
    def compute_full_voucher_name(self):
        """Cada localización definirá su método get_full_voucher_name_
        según el criterio que se requiera para armar el name
        """
        for r in self:
            r.full_voucher_name = r._get_full_voucher_name(FULL_VOUCHER_NAME_FUNC)
    
    @api.depends('full_voucher_name')
    def _compute_display_name(self):
        for r in self:
            r.display_name = r.full_voucher_name

    def get_params_for_available_vouchers(self):
        """Método genérico para pedir los parámetros de filtro de comprobantes
        Pudiendo usarse tanto para filtrar talonarios como para filtrar 
        tipos de comprobantes, usando la categoría y las denominaciones 
        (las debe agregar cada localización)

        :return: Diccionario con los parámetros
        :rtype: dict()
        """
        return self._get_default_document_book_params(DEFAULT_DOCUMENT_BOOK_FUNC)

    def get_params_for_document_books(self):
        """
        Método genérico para devolver los talonarios correspondientes a mostrar en un comprobante
        :return: Diccionario con los parámetros
        :rtype: dict()
        """
        return self._get_default_document_book_params(AVAILABLE_DOCUMENT_BOOK_FUNC)

    def _get_default_document_book_params(self, document_book_func):
        self.ensure_one()
        params = {'category': BOOK_TYPE_CATEGORIES.get(self.move_type, False)}
        if not self.company_id.country_id:
            raise ValidationError("Debe configurar un país para su compañía {}.".format(self.company_id.name))
        # Tomo el código de país de la compañía de la factura para llamar al
        # método de su localización.
        country_code = self.company_id.country_id.code.lower()
        if not ustr(country_code).encode('utf-8').isalpha():
            return params
        func = getattr(self, document_book_func + country_code, None)
        if not func:
            return params
        return func(params)

    @api.depends("pos_ar_id", "move_type")
    def compute_document_book(self):
        recs = self.filtered(lambda r: r.is_sale_document() and r.pos_ar_id)
        for rec in recs:
            params = rec.get_params_for_available_vouchers()
            rec.document_book_id = rec.pos_ar_id.get_default_document_book(params)

        (self-recs).update({'document_book_id': False})

    @api.depends("pos_ar_id", "move_type")
    def compute_pos_document_book_ids(self):
        for rec in self:
            params = rec.get_params_for_document_books()
            rec.pos_document_book_ids = rec.pos_ar_id.get_available_documents(params) if rec.pos_ar_id else None

    def _post(self, soft=True):
        res = super(AccountMove, self)._post(soft)
        for invoice in self.filtered(lambda x: x.document_book_id):

            # Obtenemos el proximo numero o validamos su estructura
            if invoice.is_sale_document() and invoice.pos_ar_id:
                # Llamamos a la funcion a ejecutarse desde el tipo de talonario,
                # de esta forma, hará lo correspondiente
                # para distintos casos (preimpreso, electronica, fiscal, etc.)
                getattr(invoice.with_context(skip_invoice_integrity_check=True), invoice.document_book_id.book_type_id.foo)()
                # Fuerzo una referencia de pago para evitar que Odoo la complete con el campo name
                invoice.payment_reference = invoice.full_voucher_name
        return res

    def action_preprint(self):
        """ Funcion para ejecutarse al validar una factura con talonario preimpreso """
        return
    
    def _get_move_display_name(self, show_ref=False):
        res = super()._get_move_display_name(show_ref)
        res = res.replace(self.name, self.full_voucher_name)
        return res

    def _compute_payments_widget_reconciled_info(self):
        """ Heredo el método para reemplazar el name del asiento por full_voucher_name """
        res = super()._compute_payments_widget_reconciled_info()
        for m in self:
            if not m.invoice_payments_widget:
                continue
            for i, data in enumerate(m.invoice_payments_widget.get('content', [])):
                move = self.browse(data.get('move_id'))
                m.invoice_payments_widget['content'][i]['ref'] = \
                    m.invoice_payments_widget['content'][i]['ref'].replace(move.name, move.full_voucher_name)
        return res

    def _compute_payments_widget_to_reconcile_info(self):
        """ Sobrescribo el método para usar full_voucher_name (no funciona por herencia)
        Líneas modificadas: 202, 205 (traducciones) y 225
        """
        for move in self:
            move.invoice_outstanding_credits_debits_widget = False
            move.invoice_has_outstanding = False

            if move.state != 'posted' \
                    or move.payment_state not in ('not_paid', 'partial') \
                    or not move.is_invoice(include_receipts=True):
                continue

            pay_term_lines = move.line_ids\
                .filtered(lambda line: line.account_id.account_type in ('asset_receivable', 'liability_payable'))

            domain = [
                ('account_id', 'in', pay_term_lines.account_id.ids),
                ('parent_state', '=', 'posted'),
                ('partner_id', '=', move.commercial_partner_id.id),
                ('reconciled', '=', False),
                '|', ('amount_residual', '!=', 0.0), ('amount_residual_currency', '!=', 0.0),
            ]

            payments_widget_vals = {'outstanding': True, 'content': [], 'move_id': move.id}

            if move.is_inbound():
                domain.append(('balance', '<', 0.0))
                payments_widget_vals['title'] = "Créditos pendientes"
            else:
                domain.append(('balance', '>', 0.0))
                payments_widget_vals['title'] = "Débitos pendientes"

            for line in self.env['account.move.line'].search(domain):

                if line.currency_id == move.currency_id:
                    # Same foreign currency.
                    amount = abs(line.amount_residual_currency)
                else:
                    # Different foreign currencies.
                    amount = line.company_currency_id._convert(
                        abs(line.amount_residual),
                        move.currency_id,
                        move.company_id,
                        line.date,
                    )

                if move.currency_id.is_zero(amount):
                    continue

                payments_widget_vals['content'].append({
                    'journal_name': line.ref or line.move_id.full_voucher_name,
                    'amount': amount,
                    'currency_id': move.currency_id.id,
                    'id': line.id,
                    'move_id': line.move_id.id,
                    'date': fields.Date.to_string(line.date),
                    'account_payment_id': line.payment_id.id,
                })

            if not payments_widget_vals['content']:
                continue

            move.invoice_outstanding_credits_debits_widget = payments_widget_vals
            move.invoice_has_outstanding = True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
