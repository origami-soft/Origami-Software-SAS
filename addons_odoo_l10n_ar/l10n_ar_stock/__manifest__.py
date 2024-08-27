# -*- coding: utf-8 -*-

{

    'name': 'l10n_ar_stock',

    'version': '1.0',

    'summary': 'Punto de venta en remitos',

    'description': 'Punto de venta en remitos',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'category': 'stock',

    'license': 'OPL-1',

    'depends': [
        'l10n_ar_point_of_sale',
        'l10n_stock_voucher_type',
    ],

    'data': [
        'data/document_book_type.xml',
        'data/voucher_type.xml',
        'views/pos_ar.xml',
        'views/stock_picking.xml',
    ],

    'installable': True,

    'auto_install': True,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
