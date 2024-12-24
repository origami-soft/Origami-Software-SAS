# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PerceptionPerception(models.Model):

    _inherit = 'perception.perception'

    @api.constrains('perception_rule_ids')
    def _check_rules(self):
        for perception in self:
            if perception.type_tax_use == 'sale' and perception.type == 'gross_income' and len(
                    perception.perception_rule_ids) > 1:
                raise ValidationError("Para este tipo de percepción solo debe existir una regla")

    perception_rule_ids = fields.One2many(
        comodel_name='perception.perception.rule',
        inverse_name='perception_id',
        string="Reglas de percepcion"
    )

    @api.onchange('type_tax_use')
    def onchange_type_tax_use(self):
        self.perception_rule_ids = [(2, rule.id) for rule in self.perception_rule_ids]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
