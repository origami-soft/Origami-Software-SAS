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

    'name': 'l10n_ar_selfprint_delivery_address',

    'version': '1.0.0',

    'description': 'Direccion de envio en el metodo de envio y en el remito autoimpresor',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'http://www.blueorange.com.ar',

    'summary': 'Direccion de envio en el metodo de envio y en remito autoimpresor',

    'category': 'Accounting',

    'depends': [

        'delivery',
        'l10n_ar_stock_picking_report',

    ],

    'data': [

        'views/delivery_carrier.xml',
        'report/report_data.xml',
        'report/stock_picking.xml',

    ],

    'active': False,

    'installable': True,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
