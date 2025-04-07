# -*- coding: utf-8 -*-

{

    'name': 'l10n_ar_dispatch_number',

    'version': '1.0.1',

    'category': '',

    'summary': 'Agrega número de despacho para remito, lotes y reporte',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'depends': [
        'sale_stock',
        'l10n_ar_electronic_invoice_report',
    ],

    'license': 'OPL-1',

    'data': [
        'views/stock_picking_views.xml',
        'views/stock_production_lot_views.xml',
        'views/report_invoice.xml',
        'views/res_config_settings_views.xml',
    ],

    'installable': True,

    'auto_install': False,

    'application': False,

    'description': 'Agrega número de despacho para remito, lotes y reporte',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
