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


class AccountTax(models.Model):
    _inherit = 'account.tax'

    def _compute_amount(self, base_amount, price_unit, quantity=1.0, product=None, partner=None):
        """ En caso de estar calculando una percepción, devuelvo 0 porque voy a generar el apunte por fuera """
        return 0 if self.amount_type == 'perception' else \
            super()._compute_amount(base_amount, price_unit, quantity, product, partner)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
