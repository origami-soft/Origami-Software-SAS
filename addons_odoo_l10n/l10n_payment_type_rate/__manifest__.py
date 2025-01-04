# -*- encoding: utf-8 -*-

{

    'name': 'l10n Payment Type Rate',

    'version': '1.0.3',

    'category': '',

    'summary': 'l10n Payment Type Rate',

    'author': 'BLUEORANGE GROUP S.R.L. / NEXIT (www.nexit.com.uy)',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [

        'l10n_payment_line_rate',
        'l10n_account_payment',

    ],

    'data': [

        'views/account_payment.xml',
        'wizard/account_payment_register_views.xml',

    ],

    'installable': True,

    'auto_install': False,

    'application': False,

    'description': 'Tasa nueva en múltiples métodos de pago',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
