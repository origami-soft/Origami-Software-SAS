# - coding: utf-8 -*-

{

    'name': 'l10n_ar_bank_reconcile',

    'version': '1.0',

    'category': '',

    'summary': 'Bank reconcile',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [

        'l10n_ar',

    ],

    'data': [

        'views/account_bank_reconcile.xml',
        'views/account_bank_reconcile_line.xml',
        'wizard/views/bank_reconcile_wizard.xml',
        'views/account_move_line.xml',
        'views/account_reconcile_move_line.xml',
        'wizard/views/bank_automatic_reconcile_wizard.xml',
        'security/ir.model.access.csv',
        'data/security.xml',

    ],

    'installable': True,

    'auto_install': False,

    'application': True,

    'description': """
Bank reconcile
======================================
* .
""",

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
