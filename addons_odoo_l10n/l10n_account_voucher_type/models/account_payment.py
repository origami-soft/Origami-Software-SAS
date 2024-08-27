# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class AccountPayment(models.Model):

    _inherit = 'account.payment'

    voucher_type_id = fields.Many2one(
        comodel_name='voucher.type',
        string='Tipo de comprobante',
        compute='_compute_voucher_type_id',
        readonly=False,
        store=True,
        # ondelete='restrict',
        ondelete='cascade',
        copy=True,
    )

    @api.depends('document_book_id')
    def _compute_voucher_type_id(self):
        for payment in self:
            payment.voucher_type_id = payment.document_book_id.voucher_type_id if payment.document_book_id else False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
