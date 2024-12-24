# -*- encoding: utf-8 -*-

{

    'name': 'L10n ar credit card installment',

    'version': '1.0',

    'category': 'Accounting',

    'summary': 'Cuotas de tarjetas de crédito',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [
        'l10n_credit_cards',
    ],

    'data': [
        'data/ir_rule.xml',
        'views/credit_card_installment.xml',
        'security/ir.model.access.csv',
    ],

    'installable': True,

    'auto_install': False,

    'description': """Cuotas de tarjetas de crédito""",

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
