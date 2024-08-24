# -*- encoding: utf-8 -*-

from . import set_up
from odoo import fields
from odoo.exceptions import ValidationError


class TestAccountPayment(set_up.SetUp):

    def _create_own_check(self):
        own_check_proxy = self.env['account.own.check']
        date_today = fields.Date.context_today(own_check_proxy)
        bank = self.env['res.bank'].new({})
        journal = self.env['account.journal'].new({
            'bank_id': bank,
            'bank_acc_number': 'Banco 1231',
            'update_posted': True
        })
        self.own_check = own_check_proxy.create({
            'name': '12345678',
            'bank_id': bank,
            'payment_type': 'common',
            'amount': 1250,
            'payment_type': 'postdated',
            'payment_date': date_today,
            'issue_date': date_today,
        })

    def setUp(self):
        super(TestAccountPayment, self).setUp()
        self._create_own_check()

    def test_constrain_checks(self):
        # No deberia haber cheques de terceros en pago a proveedores
        with self.assertRaises(ValidationError):
            self.supplier_payment.account_third_check_ids = self.third_check
        with self.assertRaises(ValidationError):
            self.customer_payment.account_own_check_ids = self.own_check

    def test_onchange_checks(self):

        # Probamos un pago de cliente
        self.customer_payment.account_third_check_ids = self.third_check
        self.customer_payment.onchange_account_third_check_ids()
        assert self.customer_payment.amount == self.third_check.amount

        # Probamos un pago de proveedor
        # Agregamos un cheque propio
        self.supplier_payment.account_own_check_ids = self.own_check
        self.supplier_payment.onchange_account_third_check_ids()
        assert self.supplier_payment.amount == self.own_check.amount
        # Agregamos un cheque de tercero
        self.supplier_payment.account_third_check_sent_ids = self.third_check
        self.supplier_payment.onchange_account_third_check_ids()
        assert self.supplier_payment.amount == self.own_check.amount + self.third_check.amount

    def test_post_supplier_payment(self):
        self.third_check.state = 'wallet'
        self.supplier_payment.account_third_check_sent_ids = self.third_check
        self.supplier_payment.account_own_check_ids = self.own_check
        self.supplier_payment.onchange_account_third_check_ids()
        self.supplier_payment.post()
        assert self.third_check.state == 'handed'
        assert self.own_check.state == 'handed'

    def test_post_invalid_supplier_payment(self):
        self.supplier_payment.account_third_check_sent_ids = self.third_check
        self.supplier_payment.account_own_check_ids = self.own_check
        self.supplier_payment.onchange_account_third_check_ids()

        # Intentamos validar el pago con el cheque propio en un estado invalido
        self.own_check.state = 'handed'
        with self.assertRaises(ValidationError):
            self.supplier_payment.post()
        self.own_check.state = 'draft'

        # Intentamos validar el pago con el cheque de tercero en un estado invalido
        self.third_check.state = 'handed'
        with self.assertRaises(ValidationError):
            self.supplier_payment.post()

    def test_post_customer_payment(self):
        self.customer_payment.account_third_check_ids = self.third_check
        self.customer_payment.onchange_account_third_check_ids()
        self.customer_payment.post()

        assert self.third_check.state == 'wallet'

    def test_post_customer_invalid_payment(self):
        self.customer_payment.account_third_check_ids = self.third_check
        self.customer_payment.onchange_account_third_check_ids()
        self.third_check.state = 'wallet'
        with self.assertRaises(ValidationError):
            self.customer_payment.post()

    def test_cancel_customer_payment(self):
        self.customer_payment.account_third_check_ids = self.third_check
        self.customer_payment.onchange_account_third_check_ids()
        self.customer_payment.post()
        self.customer_payment.cancel()
        assert self.third_check.state == 'draft'

    def test_cancel_supplier_payment(self):
        self.third_check.state = 'wallet'
        self.supplier_payment.account_third_check_sent_ids = self.third_check
        self.supplier_payment.account_own_check_ids = self.own_check
        self.supplier_payment.onchange_account_third_check_ids()
        self.supplier_payment.post()
        self.supplier_payment.cancel()

        assert self.third_check.state == 'wallet'
        assert self.own_check.state == 'draft'

    def test_cancel_invalid_customer_payment(self):
        self.customer_payment.account_third_check_ids = self.third_check
        self.customer_payment.onchange_account_third_check_ids()
        self.customer_payment.post()
        self.third_check.state = 'draft'

        with self.assertRaises(ValidationError):
            self.customer_payment.cancel()

    def test_cancel_invalid_supplier_payment(self):
        self.third_check.state = 'wallet'
        self.supplier_payment.account_third_check_sent_ids = self.third_check
        self.supplier_payment.account_own_checke_ids = self.own_check
        self.supplier_payment.onchange_account_third_check_ids()
        self.supplier_payment.post()
        self.third_check.state = 'wallet'
        self.own_check.state = 'draft'

        with self.assertRaises(ValidationError):
            self.supplier_payment.cancel()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

