# -*- coding: utf-8 -*-

{

    'name': 'l10n_ar_account_check_sale',

    'version': '1.0.3',

    'summary': 'Venta de cheques de terceros',

    'description': """
Cheques
==================================
    Venta de cheques de terceros.
    """,

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'category': 'Accounting',

    'license': 'OPL-1',

    'depends': [
        'l10n_reject_checks',
    ],

    'data': [
        'data/sold_check_data.xml',
        'views/account_third_check_view.xml',
        'views/account_sold_check_view.xml',
        'security/ir.model.access.csv',
        'data/security.xml',
        'wizard/wizard_sell_check_view.xml'
    ],

    'active': False,

    'application': False,

    'installable': True,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
