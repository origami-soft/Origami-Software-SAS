# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class ResCurrency(models.Model):

    _inherit = 'res.currency'

    need_rate = fields.Boolean(
        string='¿Lleva cotización?',
        copy=False
    )

    editable_inverse_rate = fields.Boolean(
        'Tasa inversa editable',
        help="Si se marca, se podra cargar la tasa de cambio de forma inversa"
    )
    rate = fields.Float(digits=(12, 10), compute='_compute_current_rate')

    @api.depends('rate_ids.rate')
    def _compute_current_rate(self):
        date = self._context.get('date') or fields.Datetime.now()
        for currency in self:
            currency_rate = self.env['res.currency.rate'].search([
                ('name', '<=', date),
                ('company_id', '=', self.env.company.id),
                ('currency_id', '=', currency.id)
            ], limit=1, order='name desc')
            currency.rate = currency_rate.rate or 1.0

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
