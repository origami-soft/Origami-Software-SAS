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


class StockMove(models.Model):
    _inherit = 'stock.move'
    
    def _get_arba_cot_details(self):
        self.ensure_one()
        product_qty = str(int(round(self.product_uom_qty * 100)))
        return {
            'CODIGO_UNICO_PRODUCTO': self.product_id.unique_product_code[:6], 
            'ARBA_CODIGO_UNIDAD_MEDIDA': self.product_uom.arba_uom_code,
            'CANTIDAD': product_qty,
            'PROPIO_CODIGO_PRODUCTO': self.product_id.default_code[:24],
            'PROPIO_DESCRIPCION_PRODUCTO': self.product_id.name[:39],
            'PROPIO_DESCRIPCION_UNIDAD_MEDIDA': self.product_uom.name[:19],
            'CANTIDAD_AJUSTADA': product_qty,
        }

    def _check_arba_cot_details(self):
        self.ensure_one()
        msg = f'El producto {self.product_id.name} presenta los siguientes problemas: \n'
        errors = False
        if not self.product_id.unique_product_code:
            msg += '\t - No posee código unico de producto. \n'
            errors = True 
        if not self.product_uom.arba_uom_code:
            msg += f'\t - La unidad de medida {self.product_uom.name} no poseé codigo de unidad de medida. \n'
            errors = True 
        if not self.product_id.default_code:
            msg += '\t - No posee referencia interna o codigo propio. \n'
            errors = True 
        return (errors, msg)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
