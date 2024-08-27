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

    'name': 'l10n_ar_afip_webservices_wsfe',

    'version': '1.3.4',

    'category': 'Localization',

    'summary': 'AFIP: Factura electrónica',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'http://www.blueorange.com.ar',

    'depends': [
        'invoice_currency_rate',
        'l10n_ar_afip_webservices_wsaa',
        'l10n_ar_perceptions',
        'l10n_ar_point_of_sale',
        'currency_rate_update',
    ],

    'data': [
        'views/account_move.xml',
        'views/product_product.xml',
        'views/wsfe_configuration_view.xml',
        'views/wsfe_request_detail_view.xml',
        'security/ir.model.access.csv',
        'data/document_book_type.xml',
        'data/ncm_types.xml',
        'data/security.xml',
        'wizard/account_move_reversal_view.xml',
        'wizard/afip_missed_document_wizard_view.xml'
    ],

    'installable': True,

    'auto_install': False,

    'application': True,

    'description': """
AFIP: Webservices de factura electrónica
==================================
    Factura electrónica.\n
    Configuración de puntos de venta para factura electrónica.
    """,

}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
