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

    _inherit = 'perception.perception'

    def get_afip_code(self):
        """ Devuelve el codigo de AFIP en base a la jurisdiccion """
        self.ensure_one()
        codes = {
            ('gross_income', 'nacional'): 1,
            ('gross_income', 'provincial'): 2,
            ('gross_income', 'municipal'): 3,
            ('vat', 'nacional'): 6,
        }
        return codes.get((self.type, self.jurisdiction))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
