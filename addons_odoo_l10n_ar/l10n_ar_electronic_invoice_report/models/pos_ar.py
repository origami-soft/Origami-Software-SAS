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


class PosAr(models.Model):

    _inherit = 'pos.ar'

    invoicing_address_id = fields.Many2one(
        'res.partner',
        'Dirección de facturación',
        help='Se utilizará la dirección de este partner en las facturas electrónicas'
    )
    invoice_logo = fields.Binary(
        string="Logo factura electrónica",
        help="El logo que saldrá en las facturas electrónicas de este punto de venta."
    )
    invert_colors_qr = fields.Boolean(
        string="Invertir Colores QR",
        help="Utilice este campo para invertir los colores del QR en caso de que salga al revez.",
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
