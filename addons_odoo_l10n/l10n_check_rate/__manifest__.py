# -*- encoding: utf-8 -*-

{

    'name': 'l10n Check Rate',

    'version': '1.0.1',

    'category': '',

    'summary': 'l10n Check Rate',

    'author': 'BLUEORANGE GROUP S.R.L. / NEXIT (www.nexit.com.uy)',

    'license': 'OPL-1',

    'website': 'https://www.blueorange.com.ar',

    'depends': [

        'l10n_payment_line_rate',
        'l10n_account_check',

    ],

    'data': [

        'views/account_own_check.xml',
        'views/account_third_check.xml',
        'views/account_payment.xml',
        'wizard/account_payment_register_views.xml',

    ],

    'installable': True,

    'auto_install': False,

    'application': False,

    'description': 'Tasa nueva en cheques',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
