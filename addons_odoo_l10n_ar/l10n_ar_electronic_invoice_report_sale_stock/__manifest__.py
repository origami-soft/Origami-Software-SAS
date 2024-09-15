# -*- coding: utf-8 -*-

{

    'name': 'Sale stock report electronic invoice',

    'version': '1.0',

    'category': 'Accounting',

    'summary': 'Lotes en factura electrónica',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [
        'l10n_ar_electronic_invoice_report',
        'stock_account'
    ],

    'data': [
        'report/report_electronic_invoice.xml'
    ],

    'installable': True,

    'auto_install': True,

    'application': False,

    'description': 'Lotes en factura electrónica',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
