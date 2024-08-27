# -*- encoding: utf-8 -*-

{

    'name': 'l10n Payment Line',

    'version': '1.0',

    'category': '',

    'summary': 'l10n Payment Line',

    'author': 'BLUEORANGE GROUP S.R.L. / NEXIT (www.nexit.com.uy)',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [

        'account',
        'l10n_fixed_rate',

    ],

    'data': [
        'views/account_journal.xml',
        'views/account_payment.xml',
        'views/res_config_settings.xml',
        'wizard/account_payment_register.xml',
    ],

    'installable': True,

    'auto_install': False,

    'application': False,

    'description': 'Abstracción para líneas de pago',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
