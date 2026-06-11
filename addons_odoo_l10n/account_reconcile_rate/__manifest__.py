# -*- coding: utf-8 -*-

{

    'name': 'Account Reconcile Rate',

    'version': '1.0.1',

    'category': '',

    'summary': 'Cotización en conciliaciones',

    'author': 'BLUEORANGE GROUP S.R.L. / NEXIT (www.nexit.com.uy)',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [

        'l10n_fixed_rate',
        'account_accountant',

    ],

    'data': [

        'wizard/account_reconcile_wizard.xml',

    ],

    'installable': True,

    'auto_install': True,

    'application': False,

    'description': 'Cotización en conciliaciones',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
