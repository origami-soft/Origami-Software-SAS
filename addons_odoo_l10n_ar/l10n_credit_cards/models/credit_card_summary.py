# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CreditCardSummary(models.AbstractModel):
    _name = 'credit.card.summary'
    _description = 'Documento de resumen de tarjeta de crédito'

    name = fields.Char(
        string='Nombre',
        required=True
    )
    amount = fields.Float(
        string='Monto'
    )
    credit_card_id = fields.Many2one(
        comodel_name='credit.card',
        string='Tarjeta de crédito'
    )
    payment_plan_id = fields.Many2one(
        comodel_name='credit.card.payment.plan',
        string='Plan de pagos'
    )
    payment_id = fields.Many2one(
        comodel_name='account.payment',
        string='Pago origen'
    )
    company_id = fields.Many2one(
        related='payment_id.company_id'
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Moneda',
        compute='get_currency'
    )

    def get_currency(self):
        for r in self:
            r.currency_id = r.credit_card_id.journal_id.currency_id or r.company_id.currency_id

    def generate_summary(self, line):
        """ Generacion de comprobante asociado al pago (Cupon de venta/Cuota de compra)
        en base al tipo de operacion realizada"""
        raise NotImplementedError("Funcion generate_summary no implementada para esta clase")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
