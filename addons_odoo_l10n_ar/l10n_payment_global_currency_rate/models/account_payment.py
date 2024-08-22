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


class AccountPayment(models.Model):

    _inherit = 'account.payment'

    currency_rate = fields.Float(
        string='Cotización a utilizar',
    )
    current_currency_rate = fields.Float(
        string='Cotización actual',
        compute='compute_current_currency_rate'
    )
    need_rate = fields.Boolean(
        string='Necesita cotización',
        related='currency_id.need_rate'
    )

    @api.onchange('currency_rate')
    def onchange_currency_rate(self):
        for field in self.get_payment_line_fields():
            for line in getattr(self, field).filtered(lambda x: x.currency_id == x.payment_id.company_id.currency_id):
                line.rate = self.currency_rate or self.current_currency_rate
                line.onchange_amount()

    @api.onchange('currency_id')
    def onchange_currency_currency_rate(self):
        self.currency_rate = 0

    @api.depends('currency_id', 'payment_date', 'company_id')
    def compute_current_currency_rate(self):
        """ Calculo la cotizacion actual de la moneda siempre y cuando sea distinta a la de la compañia """
        for payment in self:
            date = payment.payment_date or fields.Date.today()
            company = payment.company_id or self.env.company
            payment.current_currency_rate = self.env['res.currency']._get_conversion_rate(
                payment.currency_id,
                company.currency_id,
                company,
                date
            )

    def _prepare_payment_moves(self):
        if self.need_rate:
            if not self.currency_rate:
                self.currency_rate = self.current_currency_rate
            self = self.with_context(
                fixed_rate=self.currency_rate,
                fixed_from_currency=self.currency_id,
                fixed_to_currency=self.company_id.currency_id
            )
        return super(AccountPayment, self)._prepare_payment_moves()
    
    def reconcile_imputations(self, move_line):
        self = self.with_context(
            fixed_rate=self.currency_rate,
            fixed_from_currency=self.currency_id,
            fixed_to_currency=self.company_id.currency_id
        )
        return super(AccountPayment, self).reconcile_imputations(move_line)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
