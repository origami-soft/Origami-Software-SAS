# -*- encoding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{

    'name': 'partner_document_type',

    'version': '1.0.0',
    
    'category': 'base',

    'summary': 'Tipos de documento y validaciones para partners',

    'description': """Tipos de documento y validaciones para partners""",

    'author': 'BLUEORANGE GROUP S.R.L. / NEXIT (www.nexit.com.uy)',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [
        'account',
        'base_vat',
    ],

    'data': [
        'data/res_country.xml',
        'security/ir.model.access.csv',
        'views/partner_document_type.xml',
        'views/res_company.xml',
        'views/res_country.xml',
        'views/res_partner.xml',
    ],

    'active': False,

    'installable': True,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
