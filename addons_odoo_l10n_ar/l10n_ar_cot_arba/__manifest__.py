# -*- coding: utf-8 -*-

{

    'name': 'l10n_ar_cot_arba',

    'version': '1.2.3',

    'summary': 'Añade Código de Operación de Traslado (COT) en remitos',

    'description': 'COT en remitos',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'category': 'stock',

    'license': 'AGPL-3',

    'depends': [
        'l10n_ar_selfprint_merchandise_value',
        'l10n_ar_stock'
    ],

    'data': [
        'security/l10n_ar_cot_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/product_uom_data.xml',
        'data/res_config_settings_data.xml',
        'report/stock_picking.xml',
        'wizard/arba_cot_wizard_views.xml',
        'views/product_template_views.xml',
        'views/res_config_settings_view.xml',
        'views/stock_picking_views.xml',
        'views/stock_picking_type_views.xml',
        'views/uom_uom_views.xml',
    ],

    'installable': True,

    'auto_install': True,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
