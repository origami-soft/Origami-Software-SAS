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


class ResCountry(models.Model):

    _inherit = 'res.country'

    no_prefix = fields.Boolean(
        string='Evitar Prefijo',
        help=(
            "Tildar esta opción si para verificar si el documento de un partner "
            "asociado a este pais no se debe poner el prefijo del pais"
        )
    )

    code = fields.Char(
        string='Country Code', size=2,
        required=True,
        help='The ISO country code in two chars. \nYou can use this field for quick search.')

    _sql_constraints = [
        ('name_uniq', 'unique (name)',
         'The name of the country must be unique!'),
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
