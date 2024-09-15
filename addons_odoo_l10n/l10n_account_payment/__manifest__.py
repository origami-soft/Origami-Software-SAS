# -*- encoding: utf-8 -*-

{

    'name': 'l10n Account Payment',

    'version': '1.0',

    'category': '',

    'summary': 'l10n Account Payment',

    'author': 'BLUEORANGE GROUP S.R.L. / NEXIT (www.nexit.com.uy)',

    'license': 'OPL-1',

    'website': 'https://www.blueorange.com.ar',

    'depends': [

        'l10n_payment_line',

    ],

    'data': [

        'views/account_payment.xml',
        'views/res_config_settings.xml',
        'security/ir.model.access.csv',
        'wizard/account_payment_register.xml',

    ],

    'installable': True,

    'auto_install': False,

    'application': False,

    'description': 'Múltiples métodos de pago',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
