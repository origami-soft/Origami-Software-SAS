# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class AccountPayment(models.Model):

    _inherit = 'account.payment'

    # Los campos a continuación son reescritos en account.payment
    # aunque están presentes en account.move por las siguientes razones:
    # - document_book_id: debe calcularse de forma diferente
    # - document_book_type: no se recalcula
    # - pos_document_book_ids: debe calcularse de forma diferente
    document_book_id = fields.Many2one(
        comodel_name='document.book',
        string='Talonario',
        compute='_compute_document_book',
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
    @api.model
    def default_get(self, fields_list):
        default = super().default_get(fields_list)
        default['company_id'] = self.env.company.id
        return default

    @api.depends('full_voucher_name')
    def _compute_display_name(self):
        for r in self:
            r.display_name = r.full_voucher_name

    def get_params_for_available_vouchers(self):
        self.ensure_one()
        return {
            'category': self.payment_type == 'outbound' and 'payment_out' or
            self.payment_type == 'inbound' and 'payment_in'
        }
    
    def get_params_for_document_books(self):
        """
        Método genérico para devolver los talonarios correspondientes a mostrar en un comprobante
        :return: Diccionario con los parámetros
        :rtype: dict()
        """
        return {
            'category': self.payment_type == 'outbound' and 'payment_out' or
            self.payment_type == 'inbound' and 'payment_in'
        }

    @api.depends("journal_id", "payment_type")
    def _compute_document_book(self):
        payments_with_pos = self.filtered(lambda r: r.journal_id.pos_ar_id)
        for rec in payments_with_pos:
            params = rec.get_params_for_available_vouchers()
            rec.document_book_id = rec.pos_ar_id.get_default_document_book(params)
        (self - payments_with_pos).document_book_id = None
    
    @api.depends("pos_ar_id", "payment_type")
    def compute_pos_document_book_ids(self):
        for rec in self:
            params = rec.get_params_for_document_books()
            rec.pos_document_book_ids = rec.pos_ar_id.get_available_documents(params) if rec.pos_ar_id else None

    def _synchronize_to_moves(self, changed_fields):
        """Heredo método de sincronización de campos del pago al asiento contable.
        Ya que se necesita sincronizar el talonario, para que el método 
        _get_last_sequence_domain heredado en account_move de este mismo módulo
        pueda generar correctamente la secuencia de los movimientos. Referirse 
        a este método para más información.
        """
        res = super()._synchronize_to_moves(changed_fields)
        if 'document_book_id' in changed_fields:
            for payment in self:
                payment.move_id.write({'document_book_id': payment.document_book_id.id})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
