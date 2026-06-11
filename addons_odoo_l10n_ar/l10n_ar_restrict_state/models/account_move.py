# -*- coding: utf-8 -*-

from odoo import models
from odoo.exceptions import ValidationError



class AccountMove(models.Model):
    _inherit = "account.move"
    
    
    def button_draft(self):
        restricted = bool(self.env["ir.config_parameter"].sudo().get_param("l10n_ar_restrict_state.restrict_draft_invoices"))
        for item in self:
            if (item.state == "posted") and item.cae and restricted:
                raise ValidationError("No es posible restaurar a borrador una factura publicada y con código de confirmación CAE.")
            
        super(AccountMove, self).button_draft()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
