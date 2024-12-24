# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class PerceptionPerceptionTest(TransactionCase):

    def setUp(self):
        super(PerceptionPerceptionTest, self).setUp()

    def test_gross_income_many_lines(self):
        perception = self.env.ref('l10n_ar.1_perception_perception_iibb_caba_efectuada')
        perception.perception_rule_ids.unlink()
        self.env['perception.perception.rule'].create({
            'perception_id': perception.id,
            'not_applicable_minimum': 0,
            'minimum_tax': 0,
            'percentage': 0,
        })
        self.env['perception.perception.rule'].create({
            'perception_id': perception.id,
            'not_applicable_minimum': 0,
            'minimum_tax': 0,
            'percentage': 0,
        })
        with self.assertRaises(ValidationError):
            perception._check_rules()

    def test_delete_lines_onchange_type_tax_use(self):
        perception = self.env.ref('l10n_ar.1_perception_perception_iibb_caba_efectuada')
        self.env['perception.perception.rule'].create({
            'perception_id': perception.id,
            'not_applicable_minimum': 0,
            'minimum_tax': 0,
            'percentage': 0,
        })
        perception.onchange_type_tax_use()
        assert not perception.perception_rule_ids

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
