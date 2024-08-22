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
from ..exceptions.exceptions import InvalidNaturalRateError


class AccountAbstractPaymentLine(models.AbstractModel):
    _inherit = 'account.abstract.payment.line'

    natural_rate = fields.Float(string="Cotización", digits=(12, 6))
    rate = fields.Float(digits=(12, 10))

    def validate_natural_rate(self):
        return all(r.natural_rate >= 1 for r in self)

    @api.constrains('natural_rate')
    def check_natural_rate(self):
        if not self.validate_natural_rate():
            raise InvalidNaturalRateError("La cotización de la línea debe ser mayor o igual a 1.")

    def update_natural_rate(self):
        if not (self.rate and self.currency_id):
            self.natural_rate = 0
            return
        payment = self.payment_id
        real_rate = self.env['res.currency']._get_conversion_rate(
            payment.currency_id, self.currency_id, payment.company_id, payment.payment_date)
        self.natural_rate = self.rate if real_rate >= 1 else 1 / self.rate

    @api.onchange('natural_rate')
    def onchange_natural_rate(self):
        if not (self.natural_rate and self.currency_id):
            self.rate = 0
            return
        payment = self.payment_id
        real_rate = self.env['res.currency']._get_conversion_rate(
            payment.currency_id, self.currency_id, payment.company_id, payment.payment_date)
        self.rate = self.natural_rate if real_rate >= 1 else 1 / self.natural_rate

    @api.onchange('journal_id')
    def onchange_update_rate(self):
        res = super(AccountAbstractPaymentLine, self).onchange_update_rate()
        self.update_natural_rate()
        return res

    @api.onchange('amount', 'rate')
    def onchange_amount(self):
        res = super(AccountAbstractPaymentLine, self).onchange_amount()
        self.update_natural_rate()
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
