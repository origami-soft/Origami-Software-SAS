# -*- encoding: utf-8 -*-

from odoo import models, fields, api

VOUCHER_TYPE_CATEGORIES = {
    'out_invoice': 'invoice',
    'out_refund': 'refund',
    'in_invoice': 'invoice',
    'in_refund': 'refund'
}


class AccountMove(models.Model):
    _inherit = 'account.move'

    voucher_type_id = fields.Many2one(
        comodel_name='voucher.type',
        string='Tipo de comprobante',
        compute='compute_voucher_type',
        readonly=False,
        store=True,
        copy=False,
        check_company=True,
        ondelete='restrict'
    )
    refund_voucher_type_id = fields.Many2one(
        comodel_name='voucher.type',
        related='voucher_type_id.refund_voucher_type_id'
    )
    # Dato para filtrar los tipos de comprobante a elegir
    # en facturas de proveedor según la categoria
    voucher_type_category = fields.Char(
        compute="compute_voucher_type_category"
    )
    is_debit_note = fields.Boolean(
        string='¿Es nota de debito?',
        related='voucher_type_id.is_debit_note'
    )

    @api.depends("move_type")
    def compute_voucher_type_category(self):
        for rec in self:
            rec.voucher_type_category = VOUCHER_TYPE_CATEGORIES.get(rec.move_type, False)

    @api.depends("document_book_id")
    def compute_voucher_type(self):
        for rec in self:
            if rec.document_book_id:
                rec.voucher_type_id = rec.document_book_id.voucher_type_id
            elif not rec.pos_ar_id:
                rec.voucher_type_id = rec.get_voucher_type_id()
            else:
                rec.voucher_type_id = False

    def get_voucher_type_id(self):
        self.ensure_one()

    @api.depends("pos_ar_id", "move_type")
    def compute_document_book(self):
        for rec in self:
            if rec.move_type in ['out_invoice','out_refund']:
                voucher_id = rec.get_voucher_type_id()
                if voucher_id:
                    pos_ars = rec.env['pos.ar'].search([('document_book_ids.voucher_type_id', '=', voucher_id.id)])
                    journal_ids = rec.env['account.journal'].search([('pos_ar_id', 'in', pos_ars.ids)])
                    if journal_ids and rec.journal_id not in journal_ids:
                        rec.journal_id = journal_ids.sorted('sequence')[0]
                    elif not journal_ids:
                        rec.journal_id = rec.with_context(default_company_id=rec.company_id.id)._search_default_journal()
        return super().compute_document_book()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
