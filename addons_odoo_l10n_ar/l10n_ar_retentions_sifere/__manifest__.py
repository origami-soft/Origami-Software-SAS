# -*- coding: utf-8 -*-

{

    'name': 'Retentions SIFERE',

    'version': '1.0',

    'category': 'Accounting',

    'summary': 'Retenciones SIFERE',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [
        'l10n_ar_retentions',
        'l10n_ar_txt_reports',
        'l10n_account_voucher_type',
        'l10n_ar_afip_tables',
    ],

    'data': [
        # 'views/retention_sifere.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
    ],

    'installable': True,

    'auto_install': False,

    'application': False,

    'description': "Generación de archivo para la presentación de retenciones en aplicativo SIFERE",

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
