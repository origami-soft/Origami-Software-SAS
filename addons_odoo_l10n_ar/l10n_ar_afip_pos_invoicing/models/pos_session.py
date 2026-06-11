# -*- coding: utf-8 -*-

from odoo import models, api


class PosSession(models.Model):
    _inherit = "pos.session"

    @api.model
    def _pos_ui_models_to_load(self):
        res = super()._pos_ui_models_to_load()
        res.append('partner.document.type')
        return res
    
    def _loader_params_res_partner(self):
        vals = super()._loader_params_res_partner()
        vals["search_params"]["fields"].append("partner_document_type_id")
        return vals
    
    def _get_pos_ui_partner_document_type(self, params):
        return self.env['partner.document.type'].search_read(**params['search_params'])

    def _loader_params_partner_document_type(self):
        return {'search_params': {'domain': [], 'fields': []}}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
