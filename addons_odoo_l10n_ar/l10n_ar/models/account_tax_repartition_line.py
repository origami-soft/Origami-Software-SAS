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

from odoo import models, fields


class AccountTaxRepartitionLine(models.Model):
    _inherit = 'account.tax.repartition.line'

    amount_type = fields.Char(compute='get_amount_type')

    def get_amount_type(self):
        for r in self:
            r.amount_type = r.tax_id.amount_type

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
