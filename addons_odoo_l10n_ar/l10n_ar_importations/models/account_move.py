# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    voucher_type_importation = fields.Boolean(
        string='Tipo de comprobante de importación',
        related='voucher_type_id.is_importation_forward'
    )
    importation_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Despachante',
        copy=False
    )
    importation_operation_type = fields.Selection(
        selection=[('free_zone', 'Zona Franca'), ('exterior', 'Exterior')],
        default='exterior',
        string="Tipo de operación",
        copy=False
    )
    importation_djai = fields.Char(
        string="SIMI",
        copy=False
    )
    importation_overdue_djai_date = fields.Date(
        string="Fecha vto. SIMI",
        copy=False
    )
    importation_date = fields.Date(
        string="Fecha oficialización",
        copy=False
    )
    importation_bl = fields.Char(
        string="B/L",
        copy=False
    )
    importation_etd = fields.Date(
        string="ETD",
        copy=False
    )
    importation_eta = fields.Date(
        string="ETA",
        copy=False
    )

    @api.onchange('voucher_type_id')
    def onchange_voucher_type_importation(self):
        self.update({
            'importation_partner_id': False,
            'importation_operation_type': False,
            'importation_djai': False,
            'importation_overdue_djai_date': False,
            'importation_date': False,
            'importation_bl': False,
            'importation_etd': False,
            'importation_eta': False,
        })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
