# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class DocumentBook(models.Model):
    _inherit = 'document.book'

    cai = fields.Char('CAI')
    cai_due_date = fields.Date('Vencimiento CAI')
    cai_max_number = fields.Integer('Número máximo CAI')
    requires_cai = fields.Boolean(string="Requiere CAI", compute='get_requires_cai')

    @api.constrains('cai_max_number')
    def check_cai_max_number(self):
        if any(r.cai_max_number < 0 for r in self):
            raise ValidationError("El número máximo no puede ser negativo")

    @api.onchange('category', 'book_type_id')
    def clear_cai_fields(self):
        self.update({'cai': False, 'cai_due_date': False, 'cai_max_number': False})

    @api.depends('category', 'book_type_id')
    def get_requires_cai(self):
        for r in self:
            r.requires_cai = r.category == 'picking' and r.book_type_id.type == 'selfprint'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
