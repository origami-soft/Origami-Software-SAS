# -*- encoding: utf-8 -*-

from odoo import models, api, fields


class ResPartner(models.Model):

    _inherit = 'res.partner'

    get_wsafip_partner_data = fields.Boolean(
        'Obtener datos de AFIP',
        help='Sobrescribirá los datos fiscales del partner',
    )
    partner_data_error = fields.Boolean(
        'Error al obtener datos de AFIP',
    )

    @api.model
    def create(self, vals):
        vals.update({
            'get_wsafip_partner_data': False,
            'partner_data_error': False,
        })
        return super(ResPartner, self).create(vals)

    def write(self, vals):
        vals.update({
            'get_wsafip_partner_data': False,
            'partner_data_error': False,
        })
        return super(ResPartner, self).write(vals)

    @api.onchange('get_wsafip_partner_data')
    def onchange_get_wsafip_partner_data(self):
        if self.get_wsafip_partner_data:
            try:
                partner_data = self.env['partner.data.get.wizard'].new({
                    'vat': self.vat,
                    'company_id': self.env.company
                })
                vals = partner_data.get_data()
                vals = partner_data.load_vals(vals)
                vals.update({
                    'get_wsafip_partner_data': False,
                    'partner_data_error': False,
                })
                self.update(vals)
            except:
                self.update({
                    'get_wsafip_partner_data': False,
                    'partner_data_error': True,
                })


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
