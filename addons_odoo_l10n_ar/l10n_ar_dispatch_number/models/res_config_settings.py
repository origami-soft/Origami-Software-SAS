# -*- coding: utf-8 -*-

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    use_billing_first = fields.Boolean(
        string="Factura primero/ Entrega despues",
        config_parameter='l10n_ar_dispatch_number.use_billing_first',
        help="Permite obtener los lotes de los remitos no realizados (Casos donde se factura antes de realizar la entrega).")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
