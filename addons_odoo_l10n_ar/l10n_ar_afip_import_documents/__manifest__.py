# -*- coding: utf-8 -*-

{

    'name': 'l10n_ar_afip_import_documents',

    'version': '1.3',

    'category': 'Localization',

    'summary': 'Importación de documentos de AFIP',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [
        'l10n_ar_afip_webservices_wsfe'
    ],

    'data': [
        'wizard/afip_import_documents_wizard_view.xml',
        'security/ir.model.access.csv',
    ],

    'installable': True,

    'auto_install': False,

    'application': False,

    'description': """Importación de documentos de AFIP""",

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
