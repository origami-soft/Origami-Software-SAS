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

from odoo import models, api


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    @api.model
    def _get_fields_onchange_subtotal_model(self, price_subtotal, move_type, currency, company, date):
        if self.move_id.need_rate:
            if not self.move_id.currency_rate:
                self.move_id.currency_rate = self.move_id.current_currency_rate
            currency = currency.with_context(
                fixed_rate=self.move_id.currency_rate,
                fixed_from_currency=currency,
                fixed_to_currency=company.currency_id
            )
        return super(AccountMoveLine, self)._get_fields_onchange_subtotal_model(
            price_subtotal, move_type, currency, company, date
        )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
