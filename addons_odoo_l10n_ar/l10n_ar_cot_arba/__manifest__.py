# -*- coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{

    'name': 'l10n_ar_cot_arba',

    'version': '1.3.4',

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
