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
import math


class AccountPaymentRetention(models.Model):
    """
    Retenciones cargadas en pagos. Tener en cuenta que hay datos necesarios que se deberian desde
    el pago: Cuit, Moneda, Fecha, Tipo (Proveedor/Cliente)
    """

    _inherit = 'account.abstract.payment.line'
    _name = 'account.payment.retention'
    _description = 'Retención en pago'

    base = fields.Float(
        'Base',
    )
    aliquot = fields.Float(
        'Alicuota'
    )
    payment_date = fields.Date(
        string='Fecha',
        related='payment_id.payment_date',
        readonly=True
    )
    date = fields.Date(
        string='Fecha de retención',
    )
    partner_id = fields.Many2one(
        string='Empresa',
        related='payment_id.partner_id',
        readonly=True
    )
    retention_id = fields.Many2one(
        'retention.retention',
        'Retencion',
        ondelete='restrict',
        required=True,
    )
    certificate_no = fields.Char(
        string='Numero de certificado'
    )
    activity_id = fields.Many2one(
        'retention.activity',
        'Actividad',
    )
    type = fields.Selection(
        selection=[
            ('vat', 'IVA'),
            ('gross_income', 'Ingresos Brutos'),
            ('profit', 'Ganancias'),
            ('other', 'Otro'),
        ],
        string="Tipo",
        related='retention_id.type',
        readonly=True,
        store=True
    )
    jurisdiction = fields.Selection(
        [
            ('nacional', 'Nacional'),
            ('provincial', 'Provincial'),
            ('municipal', 'Municipal')
        ],
        string='Jurisdiccion',
        required=True,
    )

    def get_date_field(self):
        super(AccountPaymentRetention, self).get_date_field()
        return 'date'
    
    def get_observation(self):
        super(AccountPaymentRetention, self).get_observation()
        return 'certificate_no'
    
    def round_half_up(self, amount, decimal_places):
        """ Método auxiliar para redondear half-up """
        multiplier = 10 ** decimal_places
        return math.floor(round(amount * multiplier + 0.5, decimal_places)) / multiplier

    @api.onchange('base', 'aliquot')
    def onchange_aliquot(self):
        self.amount = self.round_half_up(self.base * (self.aliquot / 100), 2)

    @api.onchange('retention_id')
    def onchange_retention_id(self):
        if self.retention_id:
            self.update({
                'name': self.retention_id.name,
                'jurisdiction': self.retention_id.jurisdiction,
                'amount': 0.0,
                'base': 0.0,
            })
        else:
            self.update({
                'name': None,
                'jurisdiction': None,
                'amount': 0.0,
                'base': 0.0,
            })

    @api.onchange('type')
    def onchange_type(self):
        self.activity_id = None

    def get_first_move_line_debit_account(self):
        account_line = self.retention_id.tax_id.invoice_repartition_line_ids.filtered(lambda x: x.account_id)
        if account_line:
            return account_line[0].account_id.id
        else:
            return super(AccountPaymentRetention, self).get_first_move_line_debit_account()

    def get_first_move_line_credit_account(self):
        account_line = self.retention_id.tax_id.refund_repartition_line_ids.filtered(lambda x: x.account_id)
        if account_line:
            return account_line[0].account_id.id
        else:
            return super(AccountPaymentRetention, self).get_first_move_line_debit_account()

    def validate_journal_accounts(self):
        """ En retenciones las cuentas contables se obtienen del impuesto """
        return True

    def get_move_vals(self, payment):
        """ En retenciones la fecha del asiento contable debe ser la fecha de la retención """
        vals = super().get_move_vals(payment)
        vals['date'] = self.date
        return vals

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
