# -*- coding: utf-8 -*-

{

    'name': 'l10n_ar_imputation_report',

    'version': '1.0.0',

    'description': 'Reporte de imputación',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'summary': 'Reporte de imputación',

    'category': 'Accounting',

    'license': 'OPL-1',

    'depends': [
        'invoice_currency_rate',
        'l10n_point_of_sale',
    ],

    'data': [
        'report/imputation_report.xml',
        'report/report_imputation.xml',
    ],

    'active': False,

    'application': True,

    'installable': True,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
