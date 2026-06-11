# -*- encoding: utf-8 -*-

{

    'name': 'Cheques',

    'version': '1.0.7',

    'summary': 'Cheques propios y de terceros',

    'description': """
Cheques
==================================
    Cheques propios desde pagos.\n
    Cheques de terceros para cobros y pagos.\n
    """,

    'author': 'BLUEORANGE GROUP S.R.L. / NEXIT (www.nexit.com.uy)',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'category': 'Accounting',

    'depends': [
        'l10n_payment_line',
        'l10n_treasury',
    ],

    'data': [

        'security/ir.model.access.csv',
        'views/account_own_check.xml',
        'views/account_third_check.xml',
        'views/res_config_settings.xml',
        'views/account_payment.xml',
        'views/menu.xml',
        'wizard/account_payment_register.xml',
        'wizard/check_correct_wizard.xml',
        'security/security.xml',
        
    ],

    'active': False,

    'installable': True,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
