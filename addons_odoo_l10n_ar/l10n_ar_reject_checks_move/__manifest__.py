# -*- encoding: utf-8 -*-

{

    'name': 'l10n ar reject checks move',

    'version': '1.0',

    'summary': 'Asientos de rechazo de cheques propios y de terceros',

    'description': """
Cheques
==================================
    Asientos de rechazo de cheques propios y de terceros
    """,

    'author': 'BLUEORANGE GROUP S.R.L.',

    "website": "https://www.blueorange.com.ar",

    'category': 'Accounting',

    'license': 'OPL-1',

    'depends': [
        'l10n_deposit_slip',
        'l10n_reject_checks',
        'l10n_ar_account_check_sale',
        'l10n_ar_account_check_collect',
    ],

    'data': [
        'views/account_third_check_view.xml',
        'views/account_own_check_view.xml',
        'wizard/reject_checks_wizard.xml',
        'security/ir.model.access.csv',
    ],

    'active': False,

    'installable': True,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
