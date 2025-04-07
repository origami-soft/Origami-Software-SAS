# -*- coding: utf-8 -*-

from odoo import models


class StockMove(models.Model):
    _inherit = 'stock.move'
    
    def _get_arba_cot_details(self):
        self.ensure_one()
        product_qty = str(int(round(self.quantity * 100)))
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
