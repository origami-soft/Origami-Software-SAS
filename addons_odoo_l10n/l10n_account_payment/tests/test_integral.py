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
from datetime import date, timedelta


class TestIntegral(TransactionCase):
    def _create_sale_journal_account(self):
        self.sale_journal_account = self.env['account.account'].create({
            'code': 111001,
            'name': 'General',
            'user_type_id': self.env.ref('account.data_account_type_liquidity').id,
        })

    def _create_sale_journal(self, account):
        self.sale_journal = self.env['account.journal'].create({
            'name': 'General',
            'code': 'GEN',
            'type': 'general',
            'default_debit_account_id': account.id,
            'default_credit_account_id': account.id,
        })

    def _create_payment_journal_account(self):
        self.payment_journal_account = self.env['account.account'].create({
            'code': 111101,
            'name': 'Banco y caja',
            'user_type_id': self.env.ref('account.data_account_type_liquidity').id,
        })

    def _create_payment_journal(self, account):
        self.payment_journal = self.env['account.journal'].create({
            'name': 'Cobros y pagos',
            'code': 'CYP',
            'type': 'bank',
            'default_debit_account_id': account.id,
            'default_credit_account_id': account.id,
        })

    def _create_payment_method_journal_account(self):
        self.payment_method_journal_account = self.env['account.account'].create({
            'code': 111301,
            'name': 'Transferencia',
            'user_type_id': self.env.ref('account.data_account_type_liquidity').id,
        })

    def _create_payment_method_journal(self, account):
        self.payment_type_transfer = self.env['account.journal'].create({
            'name': 'Transferencia',
            'type': 'bank',
            'default_debit_account_id': account.id,
            'default_credit_account_id': account.id,
        })

    def _create_invoices(self):
        invoice_proxy = self.env['account.move']
        invoice_line_proxy = self.env['account.move.line']
        self.invoice = invoice_proxy.create({
            'partner_id': self.partner.id,
            'type': 'out_invoice',
        })
        self.invoice._onchange_partner_id()
        self.property_account_income_categ_id = self.env['account.account'].create({
            'code': 410000,
            'name': 'Ingresos Operativos',
            'user_type_id': self.env.ref('account.data_account_type_revenue').id,
        })
        invoice_line = invoice_line_proxy.create({
            'name': 'product_21_test',
            'price_unit': 0,
            'account_id': self.property_account_income_categ_id.id,
            'move_id': self.invoice.id,
        })
        invoice_line.with_context(check_move_validity=False).price_unit = 1000
        self.invoice.action_post()

    def setUp(self):
        super(TestIntegral, self).setUp()

        self.env.company.currency_id = self.env.ref('base.ARS')

        self._create_sale_journal_account()
        self._create_sale_journal(self.sale_journal_account)

        self._create_payment_journal_account()
        self._create_payment_journal(self.payment_journal_account)
        self.payment_journal.update_posted = True

        self.partner = self.env['res.partner'].create({
            'name': 'Partner',
            'property_account_receivable_id': self.sale_journal_account.id,
            'property_account_payable_id': self.sale_journal_account.id,
        })
        self._create_payment_method_journal_account()
        self._create_payment_method_journal(self.payment_method_journal_account)
        self._create_invoices()
        self.customer_payment = self.env['account.payment'].create({
            'partner_id': self.partner.id,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'amount': 500,
            'company_id': self.env.company.id,
            'journal_id': self.payment_journal.id,
            'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
        })
        self.supplier_payment = self.env['account.payment'].create({
            'partner_id': self.partner.id,
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'amount': 500,
            'company_id': self.env.company.id,
            'journal_id': self.payment_journal.id,
            'payment_method_id': self.env.ref('account.account_payment_method_manual_out').id,
        })

    def test_inbound_with_no_payment_methods_should_generate_move_when_posted(self):
        self.customer_payment.update({
            'destination_journal_id': self.payment_journal
        })
        self.customer_payment.post()
        assert len(self.customer_payment.move_line_ids) == 2
        assert len(self.customer_payment.move_line_ids.mapped('move_id')) == 1

    def test_inbound_with_payment_method_should_generate_two_moves_when_posted(self):
        self.customer_payment.update({
            'destination_journal_id': self.payment_journal
        })
        line = self.env['account.payment.type.line'].create({
            'journal_id': self.payment_type_transfer.id,
            'payment_id': self.customer_payment.id,
            'amount': 500
        })
        line.onchange_update_rate()
        self.customer_payment.post()
        assert len(self.customer_payment.move_line_ids) == 4
        assert len(self.customer_payment.move_line_ids.mapped('move_id')) == 2

    def test_outbound_with_no_payment_methods_should_generate_move_when_posted(self):
        self.supplier_payment.update({
            'destination_journal_id': self.payment_journal
        })
        self.supplier_payment.post()
        assert len(self.supplier_payment.move_line_ids) == 2
        assert len(self.supplier_payment.move_line_ids.mapped('move_id')) == 1

    def test_outbound_with_payment_method_should_generate_two_moves_when_posted(self):
        self.supplier_payment.update({
            'destination_journal_id': self.payment_journal
        })
        line = self.env['account.payment.type.line'].create({
            'journal_id': self.payment_type_transfer.id,
            'payment_id': self.supplier_payment.id,
            'amount': 500
        })
        line.onchange_update_rate()
        self.supplier_payment.post()
        assert len(self.supplier_payment.move_line_ids) == 4
        assert len(self.supplier_payment.move_line_ids.mapped('move_id')) == 2

    def test_payment_with_same_currency_as_company_and_method_with_different_currency(self):
        self.env['res.currency.rate'].create({'currency_id': self.env.ref('base.USD').id, 'rate': 0.1, 'name': date.today() - timedelta(days=1)})
        self.customer_payment.update({
            'destination_journal_id': self.payment_journal
        })
        self.payment_type_transfer.currency_id = self.env.ref('base.USD')
        line = self.env['account.payment.type.line'].create({
            'journal_id': self.payment_type_transfer.id,
            'payment_id': self.customer_payment.id,
            'amount': 50
        })
        self.customer_payment.onchange_update_rates()
        self.customer_payment.post()
        assert len(self.customer_payment.move_line_ids) == 4
        assert len(self.customer_payment.move_line_ids.mapped('move_id')) == 2
        assert sum(self.customer_payment.move_line_ids.mapped('debit')) == 1000
        assert sum(self.customer_payment.move_line_ids.mapped('amount_currency')) == 50

    def test_payment_with_different_currency_as_company_and_method_with_same_currency_as_company(self):
        self.env['res.currency.rate'].create({'currency_id': self.env.ref('base.USD').id, 'rate': 0.1, 'name': date.today() - timedelta(days=1)})
        self.customer_payment.update({
            'destination_journal_id': self.payment_journal
        })
        self.customer_payment.currency_id = self.env.ref('base.USD')
        line = self.env['account.payment.type.line'].create({
            'journal_id': self.payment_type_transfer.id,
            'payment_id': self.customer_payment.id,
            'amount': 5000,
        })
        self.customer_payment.onchange_update_rates()
        self.customer_payment.post()
        assert len(self.customer_payment.move_line_ids) == 4
        assert len(self.customer_payment.move_line_ids.mapped('move_id')) == 2
        assert sum(self.customer_payment.move_line_ids.mapped('debit')) == 10000
        assert sum(self.customer_payment.move_line_ids.mapped('amount_currency')) == -500

    def test_payment_with_different_currency_as_company_and_method_with_same_currency_as_payment(self):
        usd = self.env.ref('base.USD')
        self.env['res.currency.rate'].create({'currency_id': usd.id, 'rate': 0.1, 'name': date.today() - timedelta(days=1)})
        self.customer_payment.update({
            'destination_journal_id': self.payment_journal
        })
        self.customer_payment.currency_id = usd
        self.payment_type_transfer.currency_id = usd
        line = self.env['account.payment.type.line'].create({
            'journal_id': self.payment_type_transfer.id,
            'payment_id': self.customer_payment.id,
            'amount': 500,
        })
        self.customer_payment.onchange_update_rates()
        self.customer_payment.post()
        assert len(self.customer_payment.move_line_ids) == 4
        assert len(self.customer_payment.move_line_ids.mapped('move_id')) == 2
        assert sum(self.customer_payment.move_line_ids.mapped('debit')) == 10000
        assert not sum(self.customer_payment.move_line_ids.mapped('amount_currency'))

    def test_payment_with_different_currency_as_company_and_method_with_another_currency(self):
        usd = self.env.ref('base.USD')
        eur = self.env.ref('base.EUR')
        self.env['res.currency.rate'].create({'currency_id': usd.id, 'rate': 0.1, 'name': date.today() - timedelta(days=1)})
        self.env['res.currency.rate'].create({'currency_id': eur.id, 'rate': 0.08, 'name': date.today() - timedelta(days=1)})
        self.customer_payment.update({
            'destination_journal_id': self.payment_journal
        })
        self.customer_payment.currency_id = usd
        self.payment_type_transfer.currency_id = eur
        line = self.env['account.payment.type.line'].create({
            'journal_id': self.payment_type_transfer.id,
            'payment_id': self.customer_payment.id,
            'amount': 400,
        })
        self.customer_payment.onchange_update_rates()
        self.customer_payment.post()
        assert len(self.customer_payment.move_line_ids) == 4
        assert len(self.customer_payment.move_line_ids.mapped('move_id')) == 2
        assert sum(self.customer_payment.move_line_ids.mapped('debit')) == 10000
        assert sum(self.customer_payment.move_line_ids.filtered(lambda l: l.currency_id == usd).mapped('amount_currency')) == -500
        assert sum(self.customer_payment.move_line_ids.filtered(lambda l: l.currency_id == eur).mapped('amount_currency')) == 400

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
