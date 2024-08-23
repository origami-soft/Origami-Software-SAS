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


class RetentionRetention(models.Model):

    _inherit = 'account.tax.ar'
    _name = 'retention.retention'
    _description = 'Retención'

    def get_retention_groups(self):
        return self.get_retention_gross_income_groups() | \
               self.get_retention_vat_groups() | \
               self.get_retention_profit_groups()

    def get_retention_gross_income_groups(self):
        return self.env['retention.retention'].search([
            ('type', '=', 'gross_income')
        ]).mapped('tax_id.tax_group_id')

    def get_retention_vat_groups(self):
        return self.env['retention.retention'].search([
            ('type', '=', 'vat')
        ]).mapped('tax_id.tax_group_id')

    def get_retention_profit_groups(self):
        return self.env['retention.retention'].search([
            ('type', '=', 'profit')
        ]).mapped('tax_id.tax_group_id')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
