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

    'name': 'Sale stock report electronic invoice',

    'version': '1.0',

    'category': 'Accounting',

    'summary': 'Lotes en factura electrónica',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'depends': [
        'l10n_ar_electronic_invoice_report',
        'sale_stock'
    ],

    'data': [
        'report/report_electronic_invoice.xml'
    ],

    'installable': True,

    'auto_install': True,

    'application': False,

    'description': 'Lotes en factura electrónica',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
