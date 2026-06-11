# -*- coding: utf-8 -*-

{

    'name': 'l10n_ar_perceptions',

    'version': '1.3.1',

    'category': 'Accounting',

    'summary': 'Percepciones para Argentina',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [
        'l10n_ar_taxes',
        'invoice_currency_rate'
    ],

    'data': [
        'views/perception_perception.xml',
        'views/account_invoice.xml',
        'views/account_invoice_perception.xml',
        'views/product_product.xml',
        'security/ir.model.access.csv',
        'data/security.xml',
    ],

    'installable': True,

    'auto_install': False,

    'application': True,

    'description': 'Contempla percepciones en la carga de facturas',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
