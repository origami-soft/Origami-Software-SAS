# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    retention_partner_rule_ids = fields.One2many(
        comodel_name='retention.partner.rule',
        inverse_name='partner_id',
        string="Alicuotas de retenciones",
        domain=lambda l: [('company_id', 'in', l.env.companies.ids)],
    )

    @api.onchange('supplier', 'parent_id')
    def onchange_supplier_parent_id(self):
        self.retention_partner_rule_ids = [(2, rule.id) for rule in self.retention_partner_rule_ids]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
