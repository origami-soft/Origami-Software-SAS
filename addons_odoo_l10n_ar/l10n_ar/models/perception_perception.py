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


class PerceptionPerception(models.Model):

    _inherit = 'account.tax.ar'
    _name = 'perception.perception'
    _description = 'Percepción'

    def get_perception_groups(self, company):
        return self.get_perception_gross_income_groups(company) |\
               self.get_perception_vat_groups(company) |\
               self.get_perception_profit_groups(company)

    def get_perception_gross_income_groups(self, company):
        return self.env['perception.perception'].search([
            ('type', '=', 'gross_income'), ('company_id', '=', company.id)
        ]).mapped('tax_id.tax_group_id')

    def get_perception_vat_groups(self, company):
        return self.env['perception.perception'].search([
            ('type', '=', 'vat'), ('company_id', '=', company.id)
        ]).mapped('tax_id.tax_group_id')

    def get_perception_profit_groups(self, company):
        return self.env['perception.perception'].search([
            ('type', '=', 'profit'), ('company_id', '=', company.id)
        ]).mapped('tax_id.tax_group_id')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
