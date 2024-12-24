# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class ResCompanyTest(TransactionCase):

    def test_repeated_line(self):
        self.env['res.company.perception'].search([]).unlink()
        perception = self.env.ref('l10n_ar.1_perception_perception_iibb_caba_efectuada')
        self.env['res.company.perception'].create({
            'company_id': self.env.company_id.id,
            'perception_id': perception.id,
        })
        with self.assertRaises(ValidationError):
            self.env['res.company.perception'].create({
                'company_id': self.env.company_id.id,
                'perception_id': perception.id,
            })

    def setUp(self):
        super(ResCompanyTest, self).setUp()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
