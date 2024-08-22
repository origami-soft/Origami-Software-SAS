# -*- encoding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{

    'name': 'l10n_stock_voucher_type',

    'version': '1.0',

    'category': 'Tipos de comprobantes para stock',

    'summary': 'Tipos de comprobantes para stock',

    'description': 'Tipos de comprobantes para stock',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [
        'l10n_point_of_sale',
        'stock',
    ],

    'data': [
        'data/document_book_type.xml',
        'views/stock_picking_type.xml',
    ],

    'installable': True,

    'auto_install': False,

    'application': False,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
