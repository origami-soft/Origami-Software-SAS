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
