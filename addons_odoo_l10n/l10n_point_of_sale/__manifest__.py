# -*- encoding: utf-8 -*-

{

    'name': 'l10n_point_of_sale',

    'version': '1.1.10',

    'summary': 'Punto de venta para Argentina y Uruguay',

    'description': """
Modulo encargado de manejar talonarios y puntos de venta.
    """,

    'author': 'BLUEORANGE GROUP S.R.L. / NEXIT (www.nexit.com.uy)',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'category': 'Accounting',

    'depends': [
        'account',
        'l10n_voucher_type',
    ],

    'data': [
        # 'data/document_book_type.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/account_denomination.xml',
        'views/account_journal.xml',
        'views/account_move.xml',
        'views/account_move_line.xml',
        'views/account_payment.xml',
        'views/document_book.xml',
        'views/pos_ar.xml',
        'views/menu.xml',
        'views/voucher_type.xml',
        'report/invoice_report.xml',
    ],

    'post_init_hook': 'post_init_hook',

    'uninstall_hook': 'uninstall_hook',

    'active': False,    
    
    'application': False,

    'installable': True,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
