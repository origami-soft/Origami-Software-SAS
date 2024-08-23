# -*- coding: utf-8 -*-

{

    'name': 'l10n_ar',

    'version': '17.0.1.0.2',

    'countries': ['ar'],

    'icon': '/account/static/description/l10n.png',

    'summary': 'Cuentas e impuestos de Argentina',

    'description': """ Cuentas e impuestos de Argentina """,

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'category': 'Accounting/Localizations/Account Charts',

    'license': 'OPL-1',

    'depends': [
        'base_vat_ar',
        'base_codes',
    ],

    'data': [
        # 'data/company_data.xml',
        # 'data/ar_fiscal_position.xml',
        # 'data/perception_data.xml',
        # 'data/retention_data.xml',
        # 'data/bank_update.xml',
        'views/ar_fiscal_position.xml',
        'views/account_fiscal_position.xml',
        'views/account_tax_view.xml',
        'views/reports_menu.xml',
        'views/res_bank.xml',
        'views/res_company_view.xml',
        'views/res_partner_bank.xml',
        # 'views/res_partner_view.xml',
        'views/account_tax_repartition_line.xml',
        'wizard/views/update_banks_wizard.xml',
        'security/l10n_ar_security.xml',
        'security/ir.model.access.csv',
    ],

    'demo': [
        'demo/demo_company.xml',
    ],

    'active': False,

    'installable': True,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
