# -*- coding: utf-8 -*-

{

    'name': 'IVA Retenciones',

    'version': '1.0.0',

    'category': 'Accounting',

    'summary': 'IVA Retenciones',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [
        'l10n_ar_retentions',
        'l10n_ar_txt_reports',
        'l10n_ar_importations',
    ],

    'data': [
        'views/retention_iva.xml',
        'security/ir.model.access.csv',
        'data/security.xml',
    ],

    'installable': True,

    'auto_install': False,

    'application': False,

    'description': 'Contempla retenciones IVA sufridas',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
