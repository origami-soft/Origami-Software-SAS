# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import math


class ExpenseSheetPerception(models.Model):
    """
    Percepciones cargadas en reportes de gastos.
    """

    _inherit = 'account.document.tax'
    _name = 'expense.sheet.perception'
    _description = 'Percepciones de reporte de gastos'

    sheet_id = fields.Many2one('hr.expense.sheet', 'Reporte de gastos', required=True, ondelete="cascade")
    date = fields.Date(string='Fecha contable', related='sheet_id.accounting_date', store=True)
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
    company_id = fields.Many2one(related='sheet_id.company_id')
    company_currency_id = fields.Many2one(related='sheet_id.company_currency_id')
    company_currency_amount = fields.Monetary(
        "Importe en moneda de empresa",
        compute='compute_company_currency_amount',
        currency_field='company_currency_id'
    )

    @api.depends('amount', 'currency_id', 'company_id', 'date')
    def compute_company_currency_amount(self):
        for r in self:
            if r.currency_id and r.company_id and r.currency_id != r.company_currency_id:
                r.company_currency_amount = r.currency_id._convert(
                    r.amount, r.company_id.currency_id, r.company_id, r.date or fields.Date.today())
            else:
                r.company_currency_amount = r.amount

    @api.onchange('perception_id')
    def onchange_perception_id(self):
        if self.perception_id:
            self.update({
                'name': self.perception_id.name,
                'jurisdiction': self.perception_id.jurisdiction,
                'amount': 0.0,
                'base': self.sheet_id.get_perception_base() if self.sheet_id else 0.0,
            })
        else:
            self.update({
                'name': None,
                'jurisdiction': None,
                'amount': 0.0,
                'base': 0.0,
            })

    @api.constrains('perception_id', 'sheet_id')
    def constraint_perception_id(self):
        for perception in self:
            if len(perception.sheet_id.perception_ids.filtered(
                    lambda x: x.perception_id == perception.perception_id)
            ) > 1:
                raise ValidationError("No puede haber más de una percepción similar en un mismo reporte de gastos")
    
    @api.onchange('base', 'aliquot')
    def onchange_aliquot(self):
        if self.aliquot:
            self.amount = self.round_half_up(self.base * self.aliquot, 2)
    
    def round_half_up(self, amount, decimal_places):
        """ Método auxiliar para redondear half-up """
        multiplier = 10 ** decimal_places
        return math.floor(round(amount * multiplier + 0.5, decimal_places)) / multiplier

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: