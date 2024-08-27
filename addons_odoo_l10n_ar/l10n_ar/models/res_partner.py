# -*- coding: utf-8 -*-

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    iibb_number = fields.Char(string="Número de IIBB")
    start_date = fields.Date(string="Fecha de inicio de actividad")

    iibb_situation = fields.Selection(
        string="Situación de IIBB",
        selection=[('1', 'Local'),
                   ('2', 'Convenio Multilateral'),
                   ('4', 'No inscripto'),
                   ('5', 'Reg. Simplificado')],
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
