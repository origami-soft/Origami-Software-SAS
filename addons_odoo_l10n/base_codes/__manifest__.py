# -*- encoding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{

    'name': 'base_codes',

    'version': '1.0.0',
    
    'category': 'base',

    'summary': 'References of codes and aplication with models',

    'description': """Creation of table to reference models with codes and
    application, to use them on every need, for example, electronic invoice,
    reports, etc.""",

    'author': 'BLUEORANGE GROUP S.R.L. / NEXIT (www.nexit.com.uy)',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [
        'base',
    ],

    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/codes_modes_relation.xml',
    ],

    'active': False,

    'installable': True,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
