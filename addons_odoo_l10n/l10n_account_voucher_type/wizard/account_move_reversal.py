# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class AccountMoveReversal(models.TransientModel):

    _inherit = 'account.move.reversal'

    voucher_type_id = fields.Many2one(
        comodel_name='voucher.type',
        string='Tipo de comprobante'
    )

    def _get_document_book(self):
        return self.journal_id.pos_ar_id.document_book_ids.filtered(
            lambda b: b.voucher_type_id == self.voucher_type_id
        )

    @api.onchange('move_ids')
    def onchange_move_document_type(self):
        if self.move_ids:
            move = self.move_ids[0]
            self.voucher_type_id = move.refund_voucher_type_id
            params = move.get_params_for_available_vouchers()
            params['category'] = 'refund' if move.move_type == 'out_invoice' else 'invoice'
            available_voucher_types = self.voucher_type_id.get_available_voucher_types(params)
            return {'domain': {'voucher_type_id': [('id', 'in', available_voucher_types.ids)]}}

    def _prepare_default_reversal(self, move):
        res = super()._prepare_default_reversal(move)
        document_book = self._get_document_book()
        res.update({
            'voucher_type_id': self.voucher_type_id.id,
            'document_book_id': document_book.id if document_book else False
        })
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
