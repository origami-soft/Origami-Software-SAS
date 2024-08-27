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


class AccountMove(models.Model):

    _inherit = 'account.move'

    currency_rate = fields.Float(
        string='Cotización a utilizar',
        digits=(12, 6),
    )
    current_currency_rate = fields.Float(
        string='Cotización actual',
        compute='compute_current_currency_rate',
        digits=(12, 6),
    )
    need_rate = fields.Boolean(
        string='Necesita cotización',
        related='currency_id.need_rate'
    )

    @api.onchange('currency_rate')
    def onchange_currency_rate(self):
        self._onchange_currency()

    @api.onchange('currency_id')
    def onchange_currency_currency_rate(self):
        self.currency_rate = 0

    @api.depends('currency_id', 'company_currency_id', 'invoice_date')
    def compute_current_currency_rate(self):
        """ Calculo la cotizacion actual de la moneda siempre y cuando sea distinta a la de la compañia """
        for invoice in self:
            if invoice.currency_id and invoice.currency_id != invoice.company_id.currency_id:
                date = invoice.invoice_date or fields.Date.today()
                rate = self.env['res.currency']._get_conversion_rate(invoice.currency_id, invoice.company_id.currency_id, invoice.company_id, date)
                invoice.current_currency_rate = rate
            else:
                invoice.current_currency_rate = 1
    
    def _get_currency_context(self):
        if self.need_rate:
            if not self.currency_rate:
                self.currency_rate = self.current_currency_rate
            self = self.with_context(
                fixed_rate=self.currency_rate,
                fixed_from_currency=self.currency_id,
                fixed_to_currency=self.company_id.currency_id
            )
        return self

    def _recompute_dynamic_lines(self, **kwargs):
        self = self._get_currency_context()
        return super()._recompute_dynamic_lines(**kwargs)
    
    def _recompute_tax_lines(self, **kwargs):
        self = self._get_currency_context()
        return super()._recompute_tax_lines(**kwargs)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
