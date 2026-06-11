# -*- encoding: utf-8 -*-

{

    'name': 'l10n_ar_selfprint_merchandise_value',

    'version': '1.0.1',

    'category': 'Carrier',

    'summary': 'Agrega un coeficiente al transportista para calcular el valor asegurado. Este último se imprime en el remito.',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'depends': [

        'l10n_ar_selfprint_delivery_address',

    ],

    'license': 'OPL-1',

    'data': [

        'views/delivery_view.xml',
        'report/stock_picking_report.xml',

    ],

    'installable': True,

    'auto_install': False,

    'application': False,

    'description': """Agrega un coeficiente al transportista para calcular el valor asegurado. Este último se imprime en el remito.""",

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
