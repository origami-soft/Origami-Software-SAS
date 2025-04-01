# -*- encoding: utf-8 -*-

{

    'name': 'Payment imputation',

    'version': '1.4',

    'category': 'Accounting',

    'summary': 'Multiple payments imputation',

    'author': 'BLUEORANGE GROUP S.R.L. / NEXIT (www.nexit.com.uy)',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [
        'account'
    ],

    'data': [
        'views/account_payment.xml',
        'wizard/account_payment_imputation_wizard_view.xml',
        'security/ir.model.access.csv'
    ],

    'assets': {
        'web.assets_backend': [
            'payment_imputation/static/src/views/list/list_controller.js',
        ],
    },

    'installable': True,

    'auto_install': False,

    'application': False,

    'description': 'Multiple payments imputation',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
