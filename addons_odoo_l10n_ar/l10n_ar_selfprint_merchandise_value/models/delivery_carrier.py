# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'
    
    show_insurance_value = fields.Boolean(
        string='Imprimir valor del seguro',
        default=False,
    )

    coefficient_value = fields.Float(
        string='Coeficiente',
    )

    @api.onchange('show_insurance_value')
    def onchange_show_insurance_value(self):
        self.coefficient_value = 0

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
