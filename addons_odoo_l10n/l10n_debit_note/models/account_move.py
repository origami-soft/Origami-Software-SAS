# -*- encoding: utf-8 -*-

from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_default_document_book_params(self, document_book_func):
        """Heredo método para pasar como bandera que si la factura está debitando
        a otra los talonarios que se muestren o autocompleten sean de tipo de comprobante
        nota de débito.
        """
        params = super()._get_default_document_book_params(document_book_func)
        if self.debit_origin_id:
            params['debit_note'] = True
        return params

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
