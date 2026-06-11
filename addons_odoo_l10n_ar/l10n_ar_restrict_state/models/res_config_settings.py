# -*- coding: utf-8 -*-

from odoo import models, fields



class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
    
    
    restrict_draft_invoices = fields.Boolean(
        string="Restringir facturas a borrador",
        config_parameter="l10n_ar_restrict_state.restrict_draft_invoices")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
