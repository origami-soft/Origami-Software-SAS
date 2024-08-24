# -*- coding: utf-8 -*-

{

    'name': 'L10n ar retentions perceptions pdf',

    'version': '1.0.0',

    'category': '',

    'summary': 'Base para exportar percepciones y retenciones en pdf',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [
        'l10n_ar_retentions',
        'l10n_ar_perceptions',
    ],

    'data': [
        'report/document_tax_report.xml',
        'report/report_document_tax.xml',
    ],

    'installable': True,

    'auto_install': False,

    'application': True,

    'description': """Base para exportar percepciones y retenciones en pdf""",

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
