# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AfipActivity(models.Model):
    _name = 'afip.activity'
    _description = 'Actividad de AFIP'

    name = fields.Char('Nombre', required=True)
    code = fields.Char('Código', required=True)
    description = fields.Char('Descripción F883')

    @api.depends('code', 'name')
    def _compute_display_name(self):
        for r in self:
            r.display_name = ';'.join([r.code, r.name]) if r.code and r.name else r.name

    def has_valid_code(self):
        return self.code.isdigit() and len(self.code) == 6

    @api.constrains('code')
    def check_code(self):
        if any(not r.has_valid_code() for r in self):
            raise ValidationError("El código de una actividad debe ser numérico con 6 dígitos")

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if not name:
            return super().name_search(name, args, operator, limit)
        records = self.search(['|', ('code', operator, name), ('name', operator, name)], limit=limit)
        records.fetch(['display_name'])
        return [(record.id, record.display_name) for record in records]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
