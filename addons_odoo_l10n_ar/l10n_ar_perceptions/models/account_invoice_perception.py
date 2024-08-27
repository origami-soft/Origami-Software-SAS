# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import math


class AccountInvoicePerception(models.Model):
    """
    Percepciones cargadas en invoices. Tener en cuenta que hay datos necesarios que se deberian tomar
    de la invoice: Cuit, Moneda, Fecha, Tipo (Proveedor/Cliente)
    """

    _inherit = 'account.document.tax'
    _name = 'account.invoice.perception'
    _description = 'Percepciones de factura'

    move_id = fields.Many2one('account.move', 'Documento', required=True, ondelete="cascade")
    currency_id = fields.Many2one(related='move_id.currency_id')
    date_invoice = fields.Date(string='Fecha de factura', related='move_id.invoice_date', store=True)
    date_account = fields.Date(string='Fecha contable', related='move_id.date', store=True)
    partner_id = fields.Many2one(string='Empresa', related='move_id.partner_id')
    perception_id = fields.Many2one(
        'perception.perception',
        'Percepción',
        ondelete='restrict',
        required=True,
        check_company=True
    )
    jurisdiction = fields.Selection(
        [
            ('nacional', 'Nacional'),
            ('provincial', 'Provincial'),
            ('municipal', 'Municipal')
        ],
        string='Jurisdicción',
        required=True,
    )
    company_id = fields.Many2one(related='move_id.company_id')

    @api.onchange('perception_id')
    def onchange_perception_id(self):
        self.update({
            'name': self.perception_id.name,
            'jurisdiction': self.perception_id.jurisdiction,
            'amount': 0.0,
            'base': round(sum(line.price_subtotal for line in self.move_id.invoice_line_ids.filtered(
                lambda x: x.product_id and x.product_id.perception_taxable
            )), 2)
        } if self.perception_id else {
            'name': None,
            'jurisdiction': None,
            'amount': 0.0,
            'base': 0.0,
        })

    def round_half_up(self, amount, decimal_places):
        """ Método auxiliar para redondear half-up """
        multiplier = 10 ** decimal_places
        return math.floor(round(amount * multiplier + 0.5, decimal_places)) / multiplier

    @api.onchange('base', 'aliquot')
    def onchange_aliquot(self):
        if self.aliquot:
            self.amount = self.round_half_up(self.base * self.aliquot, 2)

    @api.constrains('perception_id', 'move_id')
    def constraint_perception_id(self):
        for perception in self:
            if len(perception.move_id.perception_ids.filtered(
                    lambda x: x.perception_id == perception.perception_id)
            ) > 1:
                raise ValidationError("No puede haber más de una percepcion similar en un mismo documento")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
