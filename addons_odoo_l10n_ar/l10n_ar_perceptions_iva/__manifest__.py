# -*- coding: utf-8 -*-

{

    'name': 'Perceptions Iva',

    'version': '1.0.1',

    'category': 'Accounting',

    'summary': 'Percepciones iva',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'http://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [
        'l10n_ar_perceptions',
        'l10n_ar_txt_reports',
        'l10n_ar_importations',
    ],

    'data': [
        'views/perception_iva.xml',
        'security/ir.model.access.csv',
        'data/security.xml',
    ],

    'installable': True,

    'auto_install': False,

    'application': False,

    'description': 'Contempla percepciones de IVA en proveedores',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
