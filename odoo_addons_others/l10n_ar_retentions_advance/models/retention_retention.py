# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class RetentionRetention(models.Model):
    _inherit = 'retention.retention'

    @api.constrains('retention_rule_ids')
    def _check_rules(self):
        for retention in self:
            if retention.type_tax_use == 'purchase' and retention.type == 'gross_income' \
                    and len(retention.retention_rule_ids) > 1:
                raise ValidationError("Para este tipo de retencion solo debe existir una regla")

    retention_rule_ids = fields.One2many(
        comodel_name='retention.retention.rule',
        inverse_name='retention_id',
        string="Reglas de retencion"
    )

    @api.onchange('type_tax_use')
    def onchange_type_tax_use(self):
        self.retention_rule_ids = [(2, rule.id) for rule in self.retention_rule_ids]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
