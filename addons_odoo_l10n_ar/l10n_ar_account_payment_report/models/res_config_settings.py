# -*- encoding: utf-8 -*-

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    customer_receipt_print_option = fields.Selection(
        related='company_id.customer_receipt_print_option',
        string='Imprimir en recibos de cliente',
        readonly=False,
    )
    customer_receipt_print_option_last_update = fields.Datetime(
        related='company_id.customer_receipt_print_option_last_update',
        string='Última modificación',
        readonly=True,
    )
    customer_receipt_print_option_last_user_id = fields.Many2one(
        related='company_id.customer_receipt_print_option_last_user_id',
        string='Última modificación por',
        readonly=True,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
