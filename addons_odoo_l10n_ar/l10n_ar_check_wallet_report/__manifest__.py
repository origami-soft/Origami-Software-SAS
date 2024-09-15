# -*- coding: utf-8 -*-

{

    'name': 'l10n_ar_check_wallet_report',

    'version': '1.0.0',

    'category': 'Localization',

    'summary': 'Reporte de cheques en cartera',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [

        'l10n_deposit_slip',
        'l10n_ar_account_check_sale',
        'l10n_ar_reject_checks_move',
        
    ],

    'data': [

        'security/ir.model.access.csv',
        'wizard/check_wallet_report_wizard.xml',

    ],

    'installable': True,

    'auto_install': False,

    'application': False,

    'description': """Reporte de cheques en cartera""",

}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
