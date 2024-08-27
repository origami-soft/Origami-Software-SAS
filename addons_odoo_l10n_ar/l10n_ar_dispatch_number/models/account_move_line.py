# -*- encoding: utf-8 -*-

from odoo import models

class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    def _get_invoiced_qty_per_product(self):
        res = super()._get_invoiced_qty_per_product()
        for aml in self:
            if hasattr(aml.product_id, 'bom_ids'):
                for bom_line in aml.product_id.mapped('bom_ids.bom_line_ids'):
                    res[bom_line.product_id] += 0 # Sumamos 0 para no afectar al calculo de cantidades
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
