# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class AccountMoveReversal(models.TransientModel):

    _inherit = 'account.move.reversal'

    voucher_type_id = fields.Many2one(
        comodel_name='voucher.type',
        string='Tipo de comprobante'
    )

    available_voucher_type_id = fields.Many2many(
        comodel_name='voucher.type',
        compute='_compute_available_voucher_type_id'
    )

    def _get_document_book(self):
        return self.journal_id.pos_ar_id.document_book_ids.filtered(
            lambda b: b.voucher_type_id == self.voucher_type_id
        )
    @api.depends('move_ids')
    def _compute_available_voucher_type_id(self):
        for move_reversal in self:
            if move_reversal.move_ids:
                move = move_reversal.move_ids[0]
                move_reversal.voucher_type_id = move.refund_voucher_type_id
                params = move.get_params_for_available_vouchers()
                params['category'] = 'refund' if move.move_type == 'out_invoice' else 'invoice'
                available_voucher_types = move_reversal.voucher_type_id.get_available_voucher_types(params)
                move_reversal.available_voucher_type_id = available_voucher_types
            else:
                move_reversal.available_voucher_type_id = False

    def _prepare_default_reversal(self, move):
        res = super()._prepare_default_reversal(move)
        document_book = self._get_document_book()
        res.update({
            'voucher_type_id': self.voucher_type_id.id,
            'document_book_id': document_book.id if document_book else False
        })
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
