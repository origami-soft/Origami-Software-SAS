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
from ..exceptions.exceptions import InvalidNaturalSentRateError


class AccountThirdCheck(models.Model):
    _inherit = 'account.third.check'

    natural_sent_rate = fields.Float(string="Cotización de envío", digits=(12, 6))
    sent_rate = fields.Float(digits=(12, 10))

    def validate_natural_sent_rate(self):
        return all(not r.destination_payment_id or r.natural_sent_rate >= 1 for r in self)

    @api.constrains('natural_sent_rate')
    def check_natural_sent_rate(self):
        if not self.validate_natural_sent_rate():
            raise InvalidNaturalSentRateError("La cotización de la línea debe ser mayor o igual a 1.")

    def update_natural_sent_rate(self):
        if not (self.sent_rate and self.currency_id):
            self.natural_sent_rate = 0
            return
        payment = self.destination_payment_id
        real_rate = self.env['res.currency']._get_conversion_rate(
            payment.currency_id, self.currency_id, payment.company_id, payment.payment_date or fields.Date.today())
        self.natural_sent_rate = self.sent_rate if real_rate >= 1 else 1 / self.sent_rate

    @api.onchange('natural_sent_rate')
    def onchange_natural_sent_rate(self):
        if not (self.natural_sent_rate and self.currency_id):
            self.sent_rate = 0
            return
        payment = self.destination_payment_id
        real_rate = self.env['res.currency']._get_conversion_rate(
            payment.currency_id, self.currency_id, payment.company_id, payment.payment_date or fields.Date.today())
        self.sent_rate = self.natural_sent_rate if real_rate >= 1 else 1 / self.natural_sent_rate

    @api.onchange('sent_rate')
    def onchange_sent_rate(self):
        res = super(AccountThirdCheck, self).onchange_sent_rate()
        self.update_natural_sent_rate()
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
