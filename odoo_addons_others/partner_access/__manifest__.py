# -*- coding: utf-8 -*-

{

    'name': 'partner_access',

    'version': '1.0',

    'summary': 'Accesos para Partners',

    'description': """En los partner existe la posibilidad de asociar accesos.
    """,

    'author': 'Blueorange Group S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'category': 'others',

    'license': 'OPL-1',

    'depends': [
        'mail',
    ],

    'data': [
        'data/ir_module_category.xml',
        'data/res_groups.xml',
        'views/menu.xml',
        'views/res_partner.xml',
        'views/res_partner_access.xml',
        'views/res_partner_access_category.xml',
        'security/ir.model.access.csv'
    ],

    'active': False,

    'installable': True,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
