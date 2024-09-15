# -*- encoding: utf-8 -*-

from odoo import models, fields, api
import math


class AccountPaymentRetention(models.Model):
    """
    Retenciones cargadas en pagos. Tener en cuenta que hay datos necesarios que se deberian tomar desde
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
        related='payment_id.date',
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
    journal_id = fields.Many2one(
        domain="[('company_id', '=', company_id), ('type', 'in', ['cash', 'bank']), \
                     ('payment_usage', '=', 'retention')]"
    )

    def get_date_field(self):
        return 'date'
    
    def get_observation(self):
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
        taxes = self.retention_id.get_taxes(self.company_id)
        account_line = taxes.invoice_repartition_line_ids.filtered(lambda x: x.account_id)
        if account_line:
            return account_line[0].account_id.id
        else:
            return super(AccountPaymentRetention, self).get_first_move_line_debit_account()

    def get_first_move_line_credit_account(self):
        taxes = self.retention_id.get_taxes(self.company_id)
        account_line = taxes.refund_repartition_line_ids.filtered(lambda x: x.account_id)
        if account_line:
            return account_line[0].account_id.id
        else:
            return super(AccountPaymentRetention, self).get_first_move_line_credit_account()

    def validate_journal_accounts(self):
        """ Piso el método para que se verifique si el diario de retenciones tiene las cuentas cargadas """
        for r in self.filtered(lambda l: l.journal_id):
            line_type = 'inbound' if r.payment_id.payment_type == 'inbound' else 'outbound'
            lines = getattr(r.journal_id, f'{line_type}_payment_method_line_ids')
            if not lines or any(not l.payment_account_id for l in lines):
                return False
        return True

    def get_move_vals(self, payment):
        """ En retenciones la fecha del asiento contable debe ser la fecha de la retención, y se verifica que el diario
        tenga las cuentas cargadas
        """
        self.check_journal_id()
        vals = super().get_move_vals(payment)
        vals['date'] = self.date
        return vals

    def get_line_error_description(self):
        return "Retención de {} {}".format(dict(self._fields['type'].selection).get(self.type), self.jurisdiction)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
