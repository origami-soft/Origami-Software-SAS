# - coding: utf-8 -*-

{

    'name': 'Retentions SICORE',

    'version': '1.0.2',

    'category': '',

    'summary': 'Retenciones SICORE',

    'author': 'BLUEORANGE GROUP S.R.L',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [
        'l10n_ar_retentions',
        'l10n_ar_txt_reports',
        'l10n_account_voucher_type',
        'l10n_ar_point_of_sale',
    ],

    'data': [
        'views/retention_sicore.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
    ],

    'installable': True,

    'auto_install': False,

    'application': False,

    'description': "Generación de archivo para la presentación de retenciones en aplicativo SICORE",

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
