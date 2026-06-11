# -*- coding: utf-8 -*-

{

    'name': 'l10n_ar_electronic_invoice_report',

    'version': '1.3',

    'description': 'Reporte para facturación electrónica',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'summary': 'Reporte para facturación electrónica',

    'category': 'Accounting',

    'license': 'OPL-1',

    'depends': [

        'l10n_ar_afip_webservices_wsfe',
        'l10n_ar_point_of_sale_common_report'
    ],

    'data': [
        'views/pos_ar.xml',
        'report/account_invoice_report.xml',
        'report/report_electronic_invoice.xml',
    ],

    'active': False,

    'installable': True,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
