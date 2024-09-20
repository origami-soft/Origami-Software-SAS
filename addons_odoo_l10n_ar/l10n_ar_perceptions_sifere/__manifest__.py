# -*- coding: utf-8 -*-

{

    'name': 'Perceptions SIFERE',

    'version': '1.0.1',

    'category': 'Accounting',

    'summary': 'Percepciones SIFERE',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'http://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [
        'l10n_ar_perceptions',
        'l10n_ar_txt_reports',
    ],

    'data': [
        # 'views/perception_sifere.xml',
        'security/ir.model.access.csv',
        'data/security.xml',
    ],

    'installable': True,

    'auto_install': False,

    'application': False,

    'description': 'Contempla percepciones en la carga de facturas',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
