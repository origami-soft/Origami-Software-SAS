# -*- encoding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{

    'name': 'l10n_account_voucher_type',

    'version': '1.0.0',

    'category': 'Tipos de comprobantes para contabilidad',

    'summary': 'Tipos de comprobantes para contabilidad',
    
    'description': 'Tipos de comprobantes para contabilidad',

    'author': 'BLUEORANGE GROUP S.R.L. / NEXIT (www.nexit.com.uy)',

    'website': 'https://www.blueorange.com.ar',
    
    'license': 'OPL-1',

    'depends': [
        'l10n_point_of_sale',
    ],

    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/account_move.xml',
        # 'views/account_payment.xml',
        'views/voucher_type.xml',
        'wizard/account_move_reversal.xml',
    ],

    'installable': True,

    'auto_install': False,

    'application': False,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
