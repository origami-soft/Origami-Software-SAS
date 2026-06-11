# -*- coding: utf-8 -*-

{

    'name': 'l10n ar Website Sale',

    'version': '1.1.1',

    'category': '',

    'summary': 'Posición fiscal, tipo de documento y precio sin impuestos en e-commerce',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [
        'website_sale',
        'base_vat_ar',
    ],

    'data': [
        'views/res_config_settings.xml',
        'views/templates.xml',
        'data/data.xml',
    ],

    'installable': True,

    'auto_install': True,

    'application': True,

    'description': "Posición fiscal, tipo de documento y precio sin impuestos en e-commerce",

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
