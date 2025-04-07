# -*- encoding: utf-8 -*-

{

    'name': 'L10n name followup',

    'version': '1.0.1',

    'category': 'Accounting',

    'summary': 'Numeración correcta en reportes de deuda',

    'author': 'BLUEORANGE GROUP S.R.L. / NEXIT (www.nexit.com.uy)',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [
        'l10n_point_of_sale',
        'account_followup',
    ],

    'data': [
        'views/account_followup.xml',
    ],

    'installable': True,

    'auto_install': True,

    'application': False,

    'description': 'Numeración correcta en reportes de deuda',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
