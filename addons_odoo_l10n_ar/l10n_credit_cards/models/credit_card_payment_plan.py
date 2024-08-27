# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CreditCardPaymentPlan(models.Model):
    _name = 'credit.card.payment.plan'
    _description = 'Plan de pago de tarjeta de crédito'

    name = fields.Char(
        string='Descripción',
        required=True
    )
    quantity = fields.Integer(
        string='Cantidad de cuotas',
        default=1
    )
    credit_card_id = fields.Many2one(
        comodel_name='credit.card',
        string='Tarjeta de crédito'
    )
    type = fields.Selection(
        related='credit_card_id.type'
    )
    active = fields.Boolean(
        string='Activo',
        default=True
    )

    @api.constrains('quantity')
    def check_quantity(self):
        for plan in self:
            if plan.quantity < 1:
                raise ValidationError('La cantidad de cuotas debe ser positiva.')

    _sql_constraints = [(
        'unique_name',
        'unique(name, quantity, credit_card_id)',
        'Ya existe plan de pago del mismo nombre, cantidad y tarjeta.'
    )]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
