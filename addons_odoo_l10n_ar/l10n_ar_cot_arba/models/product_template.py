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

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    unique_product_code = fields.Char('Código unico de producto')

    @api.constrains('unique_product_code')
    def check_arba_code(self):
        for rec in self.filtered('unique_product_code'):
            if len(rec.unique_product_code) != 6 or not rec.unique_product_code.isdigit():
                raise ValidationError(
                    'El código según nomenclador de ARBA debe ser de 6 dígitos'
                    ' numéricos')

    def action_arba_codes(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': 'http://www.arba.gov.ar/Aplicaciones/NomencladorTB/NomencladorTB.asp',
            'target': 'new'
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
