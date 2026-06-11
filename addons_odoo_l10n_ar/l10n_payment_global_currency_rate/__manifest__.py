# -*- coding: utf-8 -*-

{

    'name': 'L10n payment global currency rate',

    'version': '1.0.2',

    'category': '',

    'summary': 'Cotización global para pagos',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [
        'l10n_payment_line',
        'invoice_currency_rate',
        'payment_imputation',
    ],

    'data': [
        'views/account_payment.xml',
        'wizard/payment_imputation_wizard_view.xml',
        'wizard/account_payment_register.xml',
    ],

    'installable': True,

    'auto_install': False,

    'application': False,

    'description': 'Cotización global para pagos',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
