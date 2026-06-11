# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{

    'name': 'Invoice currency rate',

    'version': '1.0.3',

    'category': 'Accounting',

    'summary': 'Posibilidad de cargar cotización personalizada en facturas de otras monedas',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [
        'l10n_fixed_rate',
        'account'
    ],

    'data': [
        'views/account_move.xml',
        'views/res_currency.xml'
    ],

    'installable': True,

    'auto_install': False,

    'application': False,

    'description': 'Posibilidad de cargar cotización personalizada en facturas de otras monedas',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
