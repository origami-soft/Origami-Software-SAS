# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    iibb_number = fields.Char(related='partner_id.iibb_number', string="Número de IIBB", readonly=False)
    start_date = fields.Date(related='partner_id.start_date', string="Fecha de inicio de actividad", readonly=False)
    account_position_id = fields.Many2one('account.fiscal.position', related='partner_id.property_account_position_id', string="Posición fiscal", readonly=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
