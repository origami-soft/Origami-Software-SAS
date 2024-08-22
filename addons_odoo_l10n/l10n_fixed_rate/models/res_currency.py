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


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    def _get_conversion_rate(self, from_currency, to_currency, company, date):
        """
        Heredo la función que trae las tasas de conversión para que, en caso de que se haya pasado por contexto una
        cotización fija y la moneda de dicha cotización fija sea una de las cuales se irán a buscar cotizaciones a la
        base de datos, se devuelva dicha cotización
        """
        ctx = self.env.context
        if ctx.get('fixed_rate'):
            if from_currency == ctx['fixed_from_currency'] and to_currency == ctx['fixed_to_currency']:
                return ctx['fixed_rate']
            if from_currency == ctx['fixed_to_currency'] and to_currency == ctx['fixed_from_currency']:
                return 1 / ctx['fixed_rate']
        return super(ResCurrency, self)._get_conversion_rate(from_currency, to_currency, company, date)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
