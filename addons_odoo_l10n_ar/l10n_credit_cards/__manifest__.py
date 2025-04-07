# -*- coding: utf-8 -*-

{

    'name': 'L10n ar credit cards',

    'version': '1.0.2',

    'category': 'Accounting',

    'summary': 'Tarjetas de crédito',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [
        'l10n_payment_line',
        'l10n_treasury',
    ],

    'data': [
        'views/credit_card.xml',
        'views/res_config_settings.xml',
        'views/account_payment.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'wizard/account_payment_register.xml',
    ],

    'installable': True,

    'auto_install': False,

    'description': """Tarjetas de crédito""",

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
