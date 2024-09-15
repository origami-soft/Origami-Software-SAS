# -*- encoding: utf-8 -*-

from odoo import models, fields


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    partner_id = fields.Many2one(
        comodel_name='res.partner', 
        string='Contacto Relacionado',
    )

    def get_report_address(self):
        return self.partner_id.with_context(show_address=True).display_name.replace('\n', '<br/>')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
