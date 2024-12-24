# -*- encoding: utf-8 -*-

from odoo import models, fields


class ResPartner(models.Model):

    _inherit = 'res.partner'

    access_count = fields.Integer(
        compute='_compute_access_count',
        string='# de Accesos'
    )

    def res_partner_to_access(self):
        return {
            'name': 'Accesos',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'res.partner.access',
            'context': {'search_default_partner_id': self.parent_id.id or self.id}
        }

    def _compute_access_count(self):
        for each in self:
            partner = each.parent_id or each
            each.access_count = self.env['res.partner.access'].sudo().search_count([('partner_id', '=', partner.id)])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
