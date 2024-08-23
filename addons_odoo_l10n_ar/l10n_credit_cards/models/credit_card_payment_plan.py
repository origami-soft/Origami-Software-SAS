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
