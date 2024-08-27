# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, api


class AccountMoveReversal(models.TransientModel):

    _inherit = 'account.move.reversal'

    @api.onchange('move_id')
    def onchange_move_document_type(self):
        category = 'refund' if self.move_id.type in ['in_invoice', 'out_invoice'] else \
            ('invoice' if self.move_id.type in ['out_refund', 'in_refund'] else None)
        available_documents = self.voucher_type_id.get_available_documents(
            self.move_id.company_id.account_position_id,
            self.move_id.fiscal_position_id,
            category
        )
        self.voucher_type_id = self.move_id.voucher_type_id.refund_voucher_type_id
        return {'domain': {'voucher_type_id': [('id', 'in', available_documents.ids)]}}

    def _prepare_default_reversal(self, move):
        res = super()._prepare_default_reversal(move)
        res.update({
            'voucher_type_id': self.voucher_type_id.id,
        })
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
