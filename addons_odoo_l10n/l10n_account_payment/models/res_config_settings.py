# -*- encoding: utf-8 -*-

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    show_date_in_payment_type_line = fields.Boolean(
        related='company_id.show_date_in_payment_type_line',
        string='Mostrar fecha en métodos de pago',
        readonly=False,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
