# -*- coding: utf-8 -*-

from odoo import models


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    def _get_invoiced_qty_per_product(self):
        res = super()._get_invoiced_qty_per_product()
        for aml in self:
            for bom_line in aml.product_id.mapped('bom_ids.bom_line_ids'):
                # Sumamos 0 para no afectar al calculo de cantidades
                res[bom_line.product_id] += 0
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
