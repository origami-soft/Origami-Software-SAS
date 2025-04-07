# -*- coding: utf-8 -*-

{

    'name': 'l10n_ar_retentions',

    'version': '1.0.3',

    'category': 'Accounting',

    'summary': 'Retenciones para Argentina',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [
        'l10n_payment_line',
        'l10n_ar_taxes',
    ],

    'data': [
        'views/account_payment_retention.xml',
        'views/account_payment.xml',
        'views/res_config_settings.xml',
        'views/retention_activity.xml',
        'views/retention_retention.xml',
        'data/retention_activities.xml',
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'data/security.xml',
        'wizard/account_payment_register.xml',
    ],

    'installable': True,

    'auto_install': False,

    'application': False,

    'description': 'Contempla retenciones en la carga de pagos',

}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
