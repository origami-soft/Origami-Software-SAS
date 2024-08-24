# -*- coding: utf-8 -*-

{

    'name': 'l10n_ar_selfprint_delivery_address',

    'version': '1.0.0',

    'description': 'Dirección de envío en el método de envío y en remito autoimpresor.',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'http://www.blueorange.com.ar',

    'summary': 'Dirección de envío en el método de envío y en remito autoimpresor.',

    'category': 'Accounting',

    'depends': [

        'delivery',
        'l10n_ar_stock_picking_report',

    ],

    'data': [

        'views/delivery_carrier.xml',
        'report/report_data.xml',
        'report/stock_picking.xml',

    ],

    'active': False,

    'installable': True,

    'license': 'OPL-1',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
