# -*- coding: utf-8 -*-

{

    'name': 'l10n_ar_afip_webservices_wsaa',

    'version': '1.0',

    'category': 'Localization',

    'summary': 'Autenticacion, creacion de certificados y llaves para los ws de AFIP',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [
        'l10n_ar_afip_tables'
    ],

    'data': [
        'views/wsaa_configuration.xml',
        'security/ir.model.access.csv',
        'data/security.xml',
    ],

    'installable': True,

    'auto_install': False,

    'application': False,

    'description': """
AFIP: WebServices de autenticacion
==================================
    Creacion y configuracion de certificados y keys.\n
    Creacion y configuracion de tokens de acceso (TRA).
    """,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
