# -*- encoding: utf-8 -*-

from odoo import models, api


class RetentionRetention(models.Model):

    _inherit = 'account.tax.ar'
    _name = 'retention.retention'
    _description = 'Retención'

    def get_retention_groups(self):
        return self.get_retention_gross_income_groups() | \
               self.get_retention_vat_groups() | \
               self.get_retention_profit_groups()

    def get_retention_gross_income_groups(self):
        return self.env['retention.retention'].search([
            ('type', '=', 'gross_income')
        ]).get_taxes(self.env.company).mapped('tax_group_id')

    def get_retention_vat_groups(self):
        return self.env['retention.retention'].search([
            ('type', '=', 'vat')
        ]).get_taxes(self.env.company).mapped('tax_group_id')

    def get_retention_profit_groups(self):
        return self.env['retention.retention'].search([
            ('type', '=', 'profit')
        ]).get_taxes(self.env.company).mapped('tax_group_id')

    def get_taxes(self, company):
        return self.sudo().env['account.tax'].search([
            ('retention_id', 'in', self.ids),
            ('amount_type', '=', 'retention'),
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
