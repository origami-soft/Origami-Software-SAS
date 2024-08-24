# -*- coding: utf-8 -*-

{

    'name': 'l10n_ar_taxes',

    'version': '1.0',

    'category': 'Accounting',

    'summary': 'Manejo de importes de impuestos para Argentina',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [
        'base_codes',
        'l10n_ar'
    ],

    'data': [
        'views/account_invoice_view.xml',
        'views/taxes_menu_view.xml',
        'data/codes_modes_relation.xml',
    ],

    'assets': {
        'web.assets_backend': [
            '/l10n_ar_taxes/static/src/js/account_info_widget.js',
            '/l10n_ar_taxes/static/src/xml/account_info.xml'
        ]
    },

    'installable': True,

    'auto_install': False,

    'application': False,

    'description': 'Manejo de importes de impuestos para Argentina',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
