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

    'name': 'l10n ar Website Sale',

    'version': '1.0.1',

    'category': '',

    'summary': 'Posición fiscal y tipo de documento en e-commerce',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'depends': [
        'website_sale',
        'base_vat_ar',
    ],

    'data': [
        'templates/address.xml',
        'data/data.xml',
    ],

    'installable': True,

    'auto_install': True,

    'application': True,

    'description': """Posición fiscal y tipo de documento en e-commerce""",

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
