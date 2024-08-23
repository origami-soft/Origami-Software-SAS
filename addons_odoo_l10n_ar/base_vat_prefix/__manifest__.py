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

    'name': 'base_vat_prefix',

    'version': '17.0.1.0.2',

    'summary': 'Validation of document type without prefix',

    'description': 'Validation of document type without prefix',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'http://www.blueorange.com.ar',

    'category': 'base',

    'depends': [
        'base',
        'partner_document_type'
    ],

    'data': [
        # 'views/res_country_view.xml'
    ],

    'active': False,

    'installable': True,
    'pre_init_hook': 'pre_init_check',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
