# -*- encoding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    stock_picking_report_description = fields.Selection(selection=[
        ('self.display_name', "Operación detallada"),
        ('self.move_id.name', "Operación"),
        ('self.move_id.sale_line_id.name or self.move_id.name', "Línea de venta"),
    ], string="Descripción para autoimpresor", default='self.display_name', required=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
