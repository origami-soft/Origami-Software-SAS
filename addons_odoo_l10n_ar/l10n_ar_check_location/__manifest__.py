# -*- coding: utf-8 -*-

{

    'name': 'l10n_ar_check_location',

    'version': '1.0',

    'category': 'Localization',

    'summary': '',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [
        'l10n_account_check',
    ],

    'data': [

        'views/account_check_location.xml',
        'views/account_own_check.xml',
        'views/account_third_check.xml',
        'views/account_payment.xml',
        'security/ir.model.access.csv',
        'wizard/account_payment_register.xml',

    ],

    'installable': True,

    'auto_install': False,

    'application': True,

    'description': """
Cheques: Ubicacion en cheques
==================================
    """,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
