# -*- coding: utf-8 -*-

{

    'name': 'L10n ar credit card installment concile',

    'version': '1.0',

    'category': 'Accounting',

    'summary': 'Conciliación de cuotas de tarjetas de crédito',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [
        'l10n_credit_card_installment',
    ],

    'data': [
        'data/ir_rule.xml',
        'views/credit_card_installment.xml',
        'views/credit_card_installment_concile.xml',
        'security/ir.model.access.csv',
    ],

    'installable': True,

    'auto_install': False,

    'description': """Conciliación de cuotas de tarjetas de crédito""",

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
