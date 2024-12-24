# -*- encoding: utf-8 -*-

from odoo import models, fields


class SaleSubscription(models.Model):

    _inherit = 'sale.order'

    date_to_adjust_price = fields.Date(
        'No actualizar precios hasta:',
        help='No se actualizarán los precios de las ventas hasta la fecha seleccionada.'
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
