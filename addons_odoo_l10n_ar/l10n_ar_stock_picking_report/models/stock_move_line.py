# -*- encoding: utf-8 -*-

from odoo import models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def get_report_description(self):
        return eval(self.company_id.stock_picking_report_description)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
