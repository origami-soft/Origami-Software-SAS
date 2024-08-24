# -*- coding: utf-8 -*-

{

    'name': 'l10n_ar_account_payment_report',

    'version': '1.0.1',

    'description': 'Reporte de Pagos',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'http://www.blueorange.com.ar',

    'summary': 'Reporte de Pagos',

    'category': 'Accounting',

    'license': 'OPL-1',

    'depends': [
        'l10n_ar_point_of_sale',
        'l10n_ar_retentions',
        'payment_imputation',
    ],

    'data': [
        'report/report_account_payment.xml',
        'report/report_account_payment_data.xml',
    ],

    'active': False,

    'installable': True,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
