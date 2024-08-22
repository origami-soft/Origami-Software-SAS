# -*- coding: utf-8 -*-

{

    'name': 'l10n_ar_account_check_collect',

    'version': '1.0',

    'summary': 'Cobro de cheques propios',

    'description': """ Cobro de cheques propios """,

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'category': 'Accounting',

    'license': 'OPL-1',

    'depends': [
        'l10n_ar_check_location',
        'l10n_own_check_reconcile'
    ],

    'data': [
        'wizard/account_check_collect_wizard.xml',
        'views/account_own_check.xml',
        'security/ir.model.access.csv'
    ],

    'auto_install': False,

    'installable': True,

    'application': False,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
