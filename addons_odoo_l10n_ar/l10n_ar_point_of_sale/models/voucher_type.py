# -*- encoding: utf-8 -*-

from odoo import models


class VoucherType(models.Model):

    _inherit = 'voucher.type'

    def get_available_documents(self, issue_fiscal_position, receipt_fiscal_position, category):
        """ Devuelve los posibles comprobantes que se pueden emitir segun la posicion fiscal y categoria """
        denominations = issue_fiscal_position.get_available_denominations(receipt_fiscal_position)
        return self.sudo().search([
            ('denomination_id', 'in', denominations.ids),
            ('category', '=', category)
        ])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
