# -*- coding: utf-8 -*-
{

    'name': 'l10n_ar_afip_pos_invoicing',

    'version': '1.0',

    'description': 'Facturación argentina desde PoS',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'http://www.blueorange.com.ar',

    'summary': 'Facturación argentina desde PoS',

    'category': 'Accounting',

    'license': 'OPL-1',

    'depends': [

        'l10n_ar_afip_webservices_wsfe',
        'point_of_sale',

    ],

    'data': [

    ],

    'assets': {
        'point_of_sale._assets_pos': [
            'l10n_ar_afip_pos_invoicing/static/src/app/screens/partner_list/partner_editor/partner_editor.xml',
            'l10n_ar_afip_pos_invoicing/static/src/js/overrides/partner_editor.js',
            'l10n_ar_afip_pos_invoicing/static/src/js/overrides/pos_store.js',
        ],
    },

    'installable': True,

    'auto_install': True,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
