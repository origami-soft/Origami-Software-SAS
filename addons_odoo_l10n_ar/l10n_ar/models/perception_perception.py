# -*- encoding: utf-8 -*-

from odoo import models, api


class PerceptionPerception(models.Model):

    _inherit = 'account.tax.ar'
    _name = 'perception.perception'
    _description = 'Percepción'

    def get_perception_groups(self, company):
        return self.get_perception_gross_income_groups(company) |\
               self.get_perception_vat_groups(company) |\
               self.get_perception_profit_groups(company)

    def get_perception_gross_income_groups(self, company):
        return self.env['perception.perception'].search([
            ('type', '=', 'gross_income'),
            '|',
            ('company_id', '=', company.id),
            ('company_id', '=', False),
        ]).get_taxes(company).mapped('tax_group_id')

    def get_perception_vat_groups(self, company):
        return self.env['perception.perception'].search([
            ('type', '=', 'vat'),
            '|',
            ('company_id', '=', company.id),
            ('company_id', '=', False)
        ]).get_taxes(company).mapped('tax_group_id')

    def get_perception_profit_groups(self, company):
        return self.env['perception.perception'].search([
            ('type', '=', 'profit'),
            '|',
            ('company_id', '=', company.id),
            ('company_id', '=', False)
        ]).get_taxes(company).mapped('tax_group_id')

    def get_taxes(self, company):
        return self.sudo().env['account.tax'].search([
            ('perception_id', 'in', self.ids),
            ('amount_type', '=', 'perception'),
            '|',
            ('company_id', '=', False),
            ('company_id', '=', company.id),
        ])

    @api.model
    def unlink(self):
        for record in self:
            record.active = False
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
