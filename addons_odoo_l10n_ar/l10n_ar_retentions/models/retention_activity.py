# -*- coding: utf-8 -*-

from odoo import models, fields, api


class RetentionActivity(models.Model):
    _name = 'retention.activity'
    _description = 'Actividad de retención'

    name = fields.Char(
        string="Actividad",
        required=True,
    )

    code = fields.Integer(
        string="Código AFIP",
        required=True,
    )

    @api.depends('code', 'name')
    def _compute_display_name(self):
        for r in self:
            format_string = "{} - {}" if len(r.name) <= 40 else "{} - {}..."
            r.display_name = format_string.format(r.code, r.name[:40])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
