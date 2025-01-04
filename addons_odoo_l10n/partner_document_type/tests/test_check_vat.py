# -*- encoding: utf-8 -*-

from odoo.tests import common


class TestCheckVat(common.TransactionCase): 

    def setUp(self):
        super(TestCheckVat, self).setUp()
        self.env.ref('base.ar').no_prefix = True
        country_ar = self.env.ref('base.ar')
        self.partner_document_type = self.env['partner.document.type'].create({
            'name': 'CUIT',
        })
        
        self.partner = self.env['res.partner'].create({
            'name': 'test',
            'country_id': country_ar.id,
            'partner_document_type_id': self.partner_document_type.id,
            'vat': '30709653543',
        })

    def test_vat_no_ar_uy(self):
        """ Testeamos que no rompimos el super """
        self.partner.write({
            'country_id': self.env.ref('base.cl').id,
            'vat': 'CL76086428-5',
        })
        self.partner.check_vat()

    def test_vat_with_parent(self):
        """ Probamos que si se carga un contacto valide con el parent """
        child_partner = self.env['res.partner'].create({
            'name': 'child_partner',
            'parent_id': self.partner.id,
            'country_id': None
        })
        # Aunque no tiene pais y tienen el mismo doc deberia pasar la validacion por el parent
        assert child_partner.vat == self.partner.vat
        child_partner.check_vat()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
