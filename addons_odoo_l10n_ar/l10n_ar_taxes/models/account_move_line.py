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
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    @api.constrains('tax_ids')
    def check_more_than_one_vat_in_line(self):
        """ Se asegura que no haya mas de un impuesto tipo IVA en las lineas de factura """
        for move_line in self:
            if len(move_line.tax_ids.filtered(lambda r: r.is_vat)) > 1:
                raise ValidationError("No puede haber mas de un impuesto de tipo IVA en una linea!")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
