# -*- encoding: utf-8 -*-

{

    'name': 'Registro de débito de cheques',

    'version': '1.0.5',

    'category': '',

    'summary': 'Registro de débito de cheques propios',

    'author': 'BLUEORANGE GROUP S.R.L. / NEXIT (www.nexit.com.uy)',

    'license': 'OPL-1',

    'website': 'https://www.blueorange.com.ar',

    'depends': [
        'l10n_account_check',
    ],

    'data': [
        'wizard/wizard_own_check_reconcile.xml',
        'views/account_own_check.xml',
        'security/ir.model.access.csv',
    ],

    'installable': True,

    'auto_install': False,

    'application': False,

    'description': 'Registro de débito de cheques propios',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
