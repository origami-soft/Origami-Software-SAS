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
DEFAULT_DOCUMENT_BOOK_FUNC = 'get_params_for_available_vouchers_'
AVAILABLE_DOCUMENT_BOOK_FUNC = 'get_params_for_document_books_'


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
        # ondelete='restrict'
        ondelete='cascade',
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

    @api.depends('document_book_id')
    def _compute_name(self):
        """Evitamos que asigne numeración estándar si lleva talonario"""
        moves_with_book = self.filtered(lambda x: x.document_book_id)
        moves_with_book.filtered(lambda x: not x.name).write({'name': '/'})
        super(AccountMove, self-moves_with_book)._compute_name()

    def _post(self, soft=True):
        res = super(AccountMove, self)._post(soft)
        for invoice in self.filtered(lambda x: x.document_book_id):

            # Obtenemos el proximo numero o validamos su estructura
            if invoice.is_sale_document() and invoice.pos_ar_id:
                # Llamamos a la funcion a ejecutarse desde el tipo de talonario,
                # de esta forma, hará lo correspondiente
                # para distintos casos (preimpreso, electronica, fiscal, etc.)
                getattr(invoice, invoice.document_book_id.book_type_id.foo)()
        return res

    def action_preprint(self):
        """ Funcion para ejecutarse al validar una factura con talonario preimpreso """
        return

    def _get_last_sequence_domain(self, relaxed=False):
        where_string, param = super(AccountMove, self)._get_last_sequence_domain(relaxed=relaxed)
        # Se reemplazan ocurrencias de backslash con dobles backslash ya que PostgreSQL 
        # los interpreta de esa forma. Ver link https://stackoverflow.com/a/55544610
        if param.get('anti_regex'):
            param['anti_regex'] = param['anti_regex'].replace('\\', r'\\')
        # Los talonarios de tipo Preimpreso automático tienen en true el dato use_automatic_sequence
        # Para evitar que al hacer facturas/pagos con estos utilice la secuencia de, por ejemplo, 
        # facturas/pagos electrónicas, se excluye a los tipos de talonario electrónicos de la búsqueda 
        # de la última secuencia (tienen use_automatic_sequence en false).
        # Para las facturas/pagos que no tengan talonario también se tiene que usar la secuencia estándar, 
        # no así para las facturas de proveedor
        if (self.is_sale_document() or self.payment_id) and (not self.document_book_id or self.document_book_id.book_type_id.use_automatic_sequence):
            where_string += """ AND id NOT IN (SELECT am.id 
                                              FROM account_move AS am 
                                              JOIN document_book AS dbook ON am.document_book_id = dbook.id 
                                              JOIN document_book_type AS dbookt ON dbook.book_type_id = dbookt.id 
                                              WHERE dbookt.use_automatic_sequence != true or dbookt.use_automatic_sequence IS NULL)"""
        return where_string, param


class AccountPartialReconcile(models.Model):
    _inherit = "account.partial.reconcile"

    # ==== Reconciliation fields ====
    debit_move_id = fields.Many2one(
        comodel_name='account.move.line',
        ondelete='cascade',
        index=True, required=True)
    credit_move_id = fields.Many2one(
        comodel_name='account.move.line',
        ondelete='cascade',
        index=True, required=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
