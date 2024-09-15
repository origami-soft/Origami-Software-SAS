# -*- encoding: utf-8 -*-


{

    'name': 'Boletas de depósito',

    'version': '1.0',

    'summary': 'Depósito de cheques de terceros',

    'description': """
Cheques
==================================
    Depósito de cheques de terceros.
    """,

    'author': 'BLUEORANGE GROUP S.R.L. / NEXIT (www.nexit.com.uy)',

    'license': 'OPL-1',

    'website': 'https://www.blueorange.com.ar',

    'category': 'Accounting',

    'depends': [
        'l10n_account_check',
    ],

    'data': [
        'views/deposit_slip_view.xml',
        'views/account_check_view.xml',
        'wizard/wizard_deposit_slip_view.xml',
        'security/ir.model.access.csv',
        'data/security.xml',
    ],

    'post_init_hook': 'post_init_hook',

    'active': False,

    'application': False,

    'installable': True,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
