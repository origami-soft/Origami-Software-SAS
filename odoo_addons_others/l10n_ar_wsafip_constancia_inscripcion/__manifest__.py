# -*- coding: utf-8 -*-

{

    'name': 'AFIP Constancia Inscripción',

    'version': '1.0',

    'summary': 'Obtención de datos de contactos desde AFIP mediante CUIT/CUIL',

    'description': 'Obtención de datos de contactos desde AFIP mediante CUIT/CUIL',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'category': 'Account',

    'license': 'OPL-1',

    'depends': [
        'l10n_ar_afip_tables',
        'l10n_ar_afip_webservices_wsaa',
    ],

    'data': [
        'views/res_partner.xml',
    ],

    'active': False,

    'installable': True,

    'external_dependencies' : {
        'python' : ['w3lib'],
    },

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
