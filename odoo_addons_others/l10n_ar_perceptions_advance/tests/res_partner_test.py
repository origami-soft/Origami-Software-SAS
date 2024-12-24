# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase


class ResPartnerTest(TransactionCase):

    def setUp(self):
        super(ResPartnerTest, self).setUp()

    def test_delete_lines_onchange_supplier_parent_id(self):
        partner = self.env['res.partner'].create({'name': 'test'})
        self.env['perception.partner.rule'].create({
            'perception_id': self.env.ref('l10n_ar.1_perception_perception_iibb_caba_efectuada').id,
            'percentage': 0,
            'partner_id': partner.id
        })
        partner.onchange_customer_parent_id()
        assert not partner.perception_partner_rule_ids

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
