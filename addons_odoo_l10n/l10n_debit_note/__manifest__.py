# -*- encoding: utf-8 -*-

{

    'name': 'L10n Debit Note',

    'version': '1.0.0',

    'summary': 'Autocompletado de tipos de comprobante de nota de débito',

    'description': """
Autocompleta con un tipo de comprobante de nota de débito e igual denominación 
al de la factura original cuando se usa la acción de creación de nota de débito.
    """,

    'author': 'BLUEORANGE GROUP S.R.L. / NEXIT (www.nexit.com.uy)',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'icon': '/account/static/description/l10n.png',

    'category': 'Accounting/Accounting',

    'depends': [
        'account_debit_note',
        'l10n_point_of_sale',
    ],

    'data': [

    ],

    'active': False,    
    
    'application': False,

    'installable': True,

    'auto_install': True,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
