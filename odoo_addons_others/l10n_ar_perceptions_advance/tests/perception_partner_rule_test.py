# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class PerceptionPartnerRuleTest(TransactionCase):

    def setUp(self):
        super(PerceptionPartnerRuleTest, self).setUp()

    def test_constraint_negative_percentage(self):
        rule = self.env['perception.partner.rule'].new({'percentage': -1})
        with self.assertRaises(ValidationError):
            rule._check_percentage()

    def test_constraint_higher_than_100_percentage(self):
        rule = self.env['perception.partner.rule'].new({'percentage': 101})
        with self.assertRaises(ValidationError):
            rule._check_percentage()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
