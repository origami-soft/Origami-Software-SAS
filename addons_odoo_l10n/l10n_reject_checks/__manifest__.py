# -*- encoding: utf-8 -*-


{

    'name': 'Rechazo de cheques',

    'version': '1.0',

    'summary': 'Rechazo de cheques de terceros',

    'description': """
Cheques
==================================
    Rechazo de cheques
    """,

    'author': 'BLUEORANGE GROUP S.R.L. / NEXIT (www.nexit.com.uy)',

    'license': 'OPL-1',

    'website': 'https://www.blueorange.com.ar',

    'category': 'Accounting',

    'depends': [
        'l10n_deposit_slip',
        'l10n_own_check_reconcile',
    ],

    'data': [
        'views/account_third_check_view.xml',
        'views/account_own_check_view.xml'
    ],

    'active': False,

    'installable': True,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
