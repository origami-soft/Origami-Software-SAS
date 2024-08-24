# -*- coding: utf-8 -*-

{

    'name': 'L10n ar document tax sifere pdf',

    'version': '1.0',

    'category': '',

    'summary': 'Exportación de reporte SIFERE en pdf',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [
        'l10n_ar_perceptions_retentions_pdf',
        'l10n_ar_retentions_sifere',
        'l10n_ar_perceptions_sifere',
    ],

    'data': [
        'views/retention_sifere.xml',
        'views/perception_sifere.xml',

    ],

    'installable': True,

    'auto_install': False,

    'application': True,

    'description': """Exportación de reporte SIFERE en pdf""",

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
