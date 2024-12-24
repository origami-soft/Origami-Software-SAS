# -*- coding: utf-8 -*-

{

    'name': 'Sale subscription price adjustment',

    'version': '1.0',

    'category': 'Sale',

    'summary': 'Actualización de precios de suscripciones',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'depends': [
        'sale_subscription',
    ],

    'license': 'OPL-1',

    'data': [
        'views/sale_order.xml',
        'wizard/sale_order_price_adjustment_wizard_view.xml',
        'security/ir.model.access.csv'
    ],

    'installable': True,

    'auto_install': False,

    'application': False,

    'description': 'Actualización de precios de suscripciones',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
