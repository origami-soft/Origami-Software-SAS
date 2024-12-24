# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):

    _inherit = 'res.partner'

    perception_partner_rule_ids = fields.One2many(
        comodel_name='perception.partner.rule',
        inverse_name='partner_id',
        string="Alicuotas de percepciones",
        domain=lambda l: [('company_id', 'in', l.env.companies.ids)],
    )

    @api.onchange('parent_id')
    def onchange_customer_parent_id(self):
        self.perception_partner_rule_ids = [(2, rule.id) for rule in self.perception_partner_rule_ids]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
