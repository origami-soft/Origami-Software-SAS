# -*- encoding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import ValidationError


class SaleOrderPriceAdjustmentWizard(models.TransientModel):
    _name = 'sale.order.price.adjustment.wizard'

    adjustment_percentage = fields.Float(
        '% Ajuste',
        required=True
    )
    date_adjustment = fields.Date(
        'Fecha de ajuste',
        default=fields.Date.today(),
        help='Fecha que se tomará para determinar si corresponde ajustar o no',
        required=True
    )
    end_date_adjustment = fields.Date(
        'No actualizar precios hasta:',
        help='Fecha hasta la cual se mantendrá el nuevo precio',
    )

    def adjust_price(self):
        subscriptions = self.env['sale.order'].browse(self.env.context.get('active_ids'))
        if not self.adjustment_percentage:
            raise ValidationError("El ajuste no puede ser del 0%.")
        # Solo se ajustarán las suscripciones que la fecha de ajuste sea menor al día del ajuste.
        for subscription in subscriptions.filtered(
                lambda x: not x.date_to_adjust_price or x.date_to_adjust_price <= self.date_adjustment
        ):
            for line in subscription.order_line:
                line.price_unit += line.price_unit * self.adjustment_percentage / 100
            subscription.message_post(body="Precio actualizado por ajuste: {}%".format(self.adjustment_percentage))
            if self.end_date_adjustment:
                subscription.date_to_adjust_price = self.end_date_adjustment

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
