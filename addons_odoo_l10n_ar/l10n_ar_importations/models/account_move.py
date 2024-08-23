# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

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
    # IMPORTANTE: Este campo está deprecado. Usar voucher_name en su lugar
    importation_forward_number = fields.Char(
        string="Número despacho",
        copy=False
    )
    importation_operation_type = fields.Selection(
        selection=[('free_zone', 'Zona Franca'), ('exterior', 'Exterior')],
        default='exterior',
        string="Tipo Operación",
        copy=False
    )
    importation_djai = fields.Char(
        string="SIMI",
        copy=False
    )
    importation_overdue_djai_date = fields.Date(
        string="Fecha Vto SIMI",
        copy=False
    )
    importation_date = fields.Date(
        string="Fecha Oficialización",
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
            'importation_forward_number': False,
            'importation_operation_type': False,
            'importation_djai': False,
            'importation_overdue_djai_date': False,
            'importation_date': False,
            'importation_bl': False,
            'importation_etd': False,
            'importation_eta': False,
        })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
