# -*- encoding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{

    'name': 'l10n_voucher_type',

    'version': '1.0',

    'category': 'Tipos de comprobantes',

    'summary': 'Tipos de comprobantes',
    
    'description': 'Tipos de comprobantes',

    'author': 'BLUEORANGE GROUP S.R.L. / NEXIT (www.nexit.com.uy)',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [
        'base'
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/voucher_type.xml',
    ],

    'active': False,    

    'application': False,

    'installable': True,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
