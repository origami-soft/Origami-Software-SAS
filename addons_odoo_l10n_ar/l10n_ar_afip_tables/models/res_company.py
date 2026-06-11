# -*- encoding: utf-8 -*-

from odoo import models, fields

TAX_USES = ['sale', 'purchase']
TAX_AFIP_CODES = [('non_taxed', 1), ('exempt', 2), ('0', 3), ('10_5', 4), ('21', 5), ('27', 6), ('5', 8), ('2_5', 9)]


class ResCompany(models.Model):
    _inherit = 'res.company'

    main_activity_id = fields.Many2one('afip.activity', "Actividad principal")
    secondary_activity_ids = fields.Many2many('afip.activity', string="Actividades secundarias")
    
    def _get_vat_domain(self, amount, tax_use):
        return [
            ('is_vat', '=', True),
            ('amount', '=', amount),
            ('type_tax_use', '=', tax_use),
            ('company_id', '=', self.id),
            '|',
            ('active', '=', False),
            ('active', '=', True),
        ]

    def get_non_taxed_domain(self, tax_use):
        return [
            ('amount', '=', 0.0),
            ('amount_type', '=', 'fixed'),
            ('is_exempt', '=', False),
            ('type_tax_use', '=', tax_use),
            ('company_id', '=', self.id),
            '|',
            ('active', '=', False),
            ('active', '=', True),
        ]
    
    def get_exempt_domain(self, tax_use):
        domain = self._get_vat_domain(0.0, tax_use)
        domain.append(('is_exempt', '=', True))
        return domain

    def get_0_domain(self, tax_use):
        return self._get_vat_domain(0.0, tax_use)
    
    def get_10_5_domain(self, tax_use):
        return self._get_vat_domain(10.5, tax_use)
    
    def get_21_domain(self, tax_use):
        return self._get_vat_domain(21.0, tax_use)
    
    def get_27_domain(self, tax_use):
        return self._get_vat_domain(27.0, tax_use)
    
    def get_5_domain(self, tax_use):
        return self._get_vat_domain(5.0, tax_use)
    
    def get_2_5_domain(self, tax_use):
        return self._get_vat_domain(2.5, tax_use)
    
    def delete_tax_codes_models(self):
        self.env['codes.models.relation'].search([('name_model', '=', 'account.tax'), ('company_id', 'in', self.ids)])\
            .unlink()

    def get_codes_models_domain(self, tax, afip_code):
        return [
            ('name', '=', "Afip"),
            ('name_model', '=', 'account.tax'),
            ('id_model', '=', tax.id),
            ('code', '=', afip_code),
            ('company_id', '=', self.id),
        ]

    def create_tax_codes_models(self):
        self.ensure_one()
        codes_models_relation_proxy = self.env['codes.models.relation']
        for tax_use in TAX_USES:
            for tax, afip_code in TAX_AFIP_CODES:
                domain = getattr(self, 'get_{}_domain'.format(tax))(tax_use)
                tax_obj = self.env['account.tax'].search(domain, limit=1)
                codels_models_domain = self.get_codes_models_domain(tax_obj, afip_code)
                if tax_obj and not codes_models_relation_proxy.search_count(codels_models_domain):
                    codes_models_relation_proxy.create({
                        'name': "Afip",
                        'name_model': 'account.tax',
                        'id_model': tax_obj.id,
                        'code': afip_code,
                        'company_id': self.id,
                    })

    def unlink(self):
        self.delete_tax_codes_models()
        return super(ResCompany, self).unlink()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
