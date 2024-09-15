# -*- coding: utf-8 -*-

{

    'name': 'l10n_ar_point_of_sale',

    'version': '1.0',

    'summary': 'Punto de venta para Argentina',

    'description': """
Modulo encargado de manejar talonarios, puntos de venta y mapeo
entre posiciones fiscales y denominaciones.
    """,

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'category': 'Accounting',

    'license': 'OPL-1',

    'depends': [
        'l10n_ar_afip_tables',
        'l10n_account_voucher_type'
    ],

    'data': [
        'views/account_move.xml',
        'views/document_book.xml',
        'views/pos_ar.xml',
    ],

    'active': False,

    'installable': True,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
