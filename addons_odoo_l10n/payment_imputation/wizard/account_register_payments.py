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

from odoo import models


class AccountPaymentRegister(models.TransientModel):

    _inherit = 'account.payment.register'

    def _prepare_payment_vals(self, invoices):
        values = super(AccountPaymentRegister, self)._prepare_payment_vals(invoices)
        lines = self.env['account.move.line']
        for invoice in invoices:
            lines |= invoice.mapped('line_ids').filtered(
                lambda r: not r.reconciled and r.account_id.internal_type in ('payable', 'receivable')
            )
        debit_lines = [(0, 0, {
            'move_line_id': line.id,
            'amount': abs(line.amount_residual),
            'concile': True,
        }) for line in lines]
        values['payment_imputation_ids'] = debit_lines or [(6, 0, [])]
        return values

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
