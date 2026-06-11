# -*- encoding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.TransientModel):
    _inherit = 'res.config.settings'

    stock_picking_report_description = fields.Selection(
        related='company_id.stock_picking_report_description',
        readonly=False
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
