# -*- coding: utf-8 -*-

{

    'name': 'l10n_ar_stock_picking_report',

    'version': '1.0.2',

    'summary': 'Reporte de remito autoimpresor',

    'description': 'Reporte de remito autoimpresor',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'category': 'stock',

    'license': 'OPL-1',

    'depends': [
        'l10n_ar_stock',
        'sale_stock',
        'l10n_ar_point_of_sale_common_report'
    ],

    'data': [
        'report/report_data.xml',
        'report/report_layout.xml',
        'views/stock_picking.xml',
    ],

    'installable': True,

    'auto_install': True,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
