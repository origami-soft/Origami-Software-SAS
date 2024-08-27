# -*- encoding: utf-8 -*-

from odoo import fields
from odoo.exceptions import ValidationError
from .test_deposit_slip import TestDepositSlip


class TestWizardDepositSlip(TestDepositSlip):

    def setUp(self):
        super(TestWizardDepositSlip, self).setUp()
        slip_proxy = self.env['wizard.deposit.slip']
        date_today = fields.Date.context_today(slip_proxy)
        journal = self.env['account.journal'].new({'update_posted': True})
        check_ids = [self.third_check.id, self.third_check_2.id]
        self.wizard_deposit_slip = slip_proxy.with_context(active_ids=check_ids).create({
            'journal_id': journal.id,
            'date': date_today
        })

    def test_create_deposit_slip(self):
        self.deposit_slip.check_ids = None
        res = self.wizard_deposit_slip.action_create_deposit_slip()
        deposit_slip = self.env['account.deposit.slip'].browse(res.get('res_id'))
        assert deposit_slip.date == self.wizard_deposit_slip.date
        assert deposit_slip.journal_id == self.wizard_deposit_slip.journal_id
        assert deposit_slip.amount == self.wizard_deposit_slip.total
        assert deposit_slip.check_ids == self.third_check | self.third_check_2
        assert deposit_slip.state == 'draft'
        assert deposit_slip.currency_id == self.wizard_deposit_slip.currency_id

    def test_create_deposit_slip_currencies(self):
        usd = self.env.ref('base.USD')
        self.third_check.currency_id = usd.id
        with self.assertRaises(ValidationError):
            self.wizard_deposit_slip.get_currency()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
