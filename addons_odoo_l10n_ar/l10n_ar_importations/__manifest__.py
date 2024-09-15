# -*- coding: utf-8 -*-

{

    'name': 'L10n ar importations',

    'version': '1.0.0',

    'category': 'Account',

    'summary': 'Datos de despachante',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [
        'l10n_ar_point_of_sale',
    ],

    'data': [
        'data/voucher_type.xml',
        'views/voucher_type.xml',
        'views/account_move.xml',
    ],

    'installable': True,

    'auto_install': False,

    'application': False,

    'description': 'Datos de despacho en la factura para luego poder informar los datos',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
