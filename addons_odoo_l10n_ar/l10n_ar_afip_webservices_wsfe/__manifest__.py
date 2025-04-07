# -*- coding: utf-8 -*-

{

    'name': 'l10n_ar_afip_webservices_wsfe',

    'version': '1.1',

    'category': 'Localization',

    'summary': 'AFIP: Factura electrónica',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [
        'invoice_currency_rate',
        'l10n_ar_afip_webservices_wsaa',
        'l10n_ar_perceptions',
        'l10n_ar_point_of_sale',
        'currency_rate_update',
        'l10n_no_delete_published_invoices'
    ],

    'data': [
        'views/account_move.xml',
        'views/pos_ar.xml',
        'views/product_product.xml',
        'views/wsfe_request_detail_view.xml',
        'security/ir.model.access.csv',
        'data/document_book_type.xml',
        'data/ncm_types.xml',
        'wizard/account_move_reversal_view.xml',
        'wizard/afip_missed_document_wizard_view.xml',
    ],

    'installable': True,

    'auto_install': False,

    'application': False,

    'description': """
AFIP: Webservices de factura electrónica
==================================
    Factura electrónica.\n
    Configuración de puntos de venta para factura electrónica.
    """,

}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
