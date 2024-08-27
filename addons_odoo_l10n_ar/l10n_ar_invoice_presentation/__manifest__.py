# -*- coding: utf-8 -*-

{

    'name': 'Account invoice presentation',

    'version': '1.0.2',

    'category': 'Account',

    'summary': 'Presentacion ventas/compras y libro de iva digital',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [
        'l10n_ar_importations',
        'l10n_ar_perceptions',
        'l10n_ar_point_of_sale',
    ],

    'data': [
        'views/account_invoice_presentation.xml',
        'views/account_invoice_vat_digital_book.xml',
        'security/ir.model.access.csv',
        'data/security.xml',
    ],

    'installable': True,

    'auto_install': False,

    'application': True,

    'description': 'Presentacion ventas/compras y libro de iva digital',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
