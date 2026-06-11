# -*- encoding: utf-8 -*-

class GeneralData:
    def __init__(self, proxy=None, company_id=None):
        self.proxy = proxy
        self.get_general_data(company_id)

    # Datos del sistema
    def get_general_data(self, company_id):
        """
        Obtiene valores predeterminados de la localizacion
        """
        company = company_id or self.proxy.env.company
        tax_group_internal = self.proxy.env['account.tax'].get_internal_tax_group(company)
        vat_no_gravado_compras = self.proxy.env['account.tax'].get_tax_by_company_and_name(company, 'Compras No gravado')
        vat_no_gravado_ventas = self.proxy.env['account.tax'].get_tax_by_company_and_name(company, 'Ventas No gravado')
        self.type_b = self.proxy.env.ref('l10n_ar_afip_tables.account_denomination_b')
        self.type_c = self.proxy.env.ref('l10n_ar_afip_tables.account_denomination_c')
        self.type_d = self.proxy.env.ref('l10n_ar_afip_tables.account_denomination_d')
        self.type_i = self.proxy.env.ref('l10n_ar_afip_tables.account_denomination_i')
        self.tax_group_internal = tax_group_internal
        self.tax_purchase_ng = vat_no_gravado_compras
        self.tax_sale_ng = vat_no_gravado_ventas
        self.codes_model_proxy = self.proxy.env['codes.models.relation']
        self.fiscal_position_nc = self.proxy.env.ref("l10n_ar_bo.ar_fiscal_position_no_categ")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
