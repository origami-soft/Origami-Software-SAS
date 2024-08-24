# -*- coding: utf-8 -*-

{

    'name': 'l10n_ar_afip_tables',

    'version': '1.2',

    'summary': 'Datas of tables of afip V.0 25082010-5',

    'description': """ Datas of tables of afip V.0 25082010-5,
mapped with models using base_codes application
""",

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'category': 'base',

    'license': 'OPL-1',

    'depends': [
        'l10n_ar',
        'uom',
        'l10n_account_voucher_type',
    ],

    'data': [
        # 'views/account_denomination.xml',
        # 'views/ar_fiscal_position.xml',
        # 'views/afip_tables_configuration.xml',
        # 'views/voucher_type.xml',
        # 'views/account_move.xml',
        # 'data/res_country_state.xml',
        # 'data/res_country.xml',
        # 'data/product_uom.xml',
        # 'data/res_currency.xml',
        # 'data/account_denomination.xml',
        # 'data/voucher_type.xml',
        # 'data/partner_document_type.xml',
        # 'data/ar_fiscal_position.xml',
        # 'data/afip_concept.xml',
        # 'data/denomination_fiscal_position.xml',
        'security/ir.model.access.csv',
    ],

    # 'post_init_hook': 'post_init_hook',
    #
    # 'uninstall_hook': 'uninstall_hook',

    'active': False,

    'installable': True,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
