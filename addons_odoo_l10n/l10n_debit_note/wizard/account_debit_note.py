# -*- encoding: utf-8 -*-

from odoo import models


class AccountDebitNote(models.TransientModel):
    _inherit = 'account.debit.note'

    def _prepare_default_values(self, move):
        """Heredo el método para calcular el talonario de la nota de débito.
        Teniendo en cuenta que:
        - Debe ser un talonario de Factura.
        - Su tipo de comprobante debe ser de nota de débito.
        - Tiene que tener la misma denominación que la factura de origen.
        """
        default_values = super()._prepare_default_values(move)
        if self.journal_id.pos_ar_id:
            params = {
                'category': 'invoice',
                'debit_note': True,
                'denomination_ids': [move.voucher_type_id.denomination_id.id],
            }
            dbook = self.journal_id.pos_ar_id.get_default_document_book(params)
            if dbook:
                default_values.update({
                    'document_book_id': dbook.id,
                    'voucher_type_id': dbook.voucher_type_id.id,
                })
        return default_values

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
