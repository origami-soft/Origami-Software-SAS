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

from odoo.tests.common import TransactionCase


class TestResCurrency(TransactionCase):
    def setUp(self):
        super(TestResCurrency, self).setUp()
        self.ars = self.env.ref('base.ARS')
        self.usd = self.env.ref('base.USD')
        self.env.company.currency_id = self.ars
        self.rate = self.env['res.currency.rate'].create({'currency_id': self.usd.id, 'rate': 0.1})

    def test_convert_with_no_context_should_return_rate_normally(self):
        assert self.ars._convert(1, self.usd, self.rate.company_id, self.rate.name) == 0.1

    def test_convert_with_fixed_rate_and_currencies_in_context_should_return_rate_in_context(self):
        self.ars = self.ars.with_context(fixed_rate=0.15, fixed_from_currency=self.ars, fixed_to_currency=self.usd)
        assert self.ars._convert(1, self.usd, self.rate.company_id, self.rate.name) == 0.15

    def test_convert_with_fixed_rate_and_inverted_currencies_in_context_should_return_inverse_rate_in_context(self):
        self.ars = self.ars.with_context(fixed_rate=0.2, fixed_from_currency=self.usd, fixed_to_currency=self.ars)
        assert self.ars._convert(1, self.usd, self.rate.company_id, self.rate.name) == 5.0

    def test_convert_with_fixed_rate_and_another_currency_in_context_should_return_rate_in_context(self):
        self.ars = self.ars.with_context(fixed_rate=0.15, fixed_from_currency=self.ars, fixed_to_currency=self.env.ref('base.EUR'))
        assert self.ars._convert(1, self.usd, self.rate.company_id, self.rate.name) == 0.1

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
