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

    'name': 'l10n_account_voucher_type',

    'version': '1.0.1',

    'category': 'Tipos de comprobantes para contabilidad',

    'summary': 'Tipos de comprobantes para contabilidad',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'depends': [
        'l10n_voucher_type',
        'account'
    ],

    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/account_move.xml',
        'views/voucher_type.xml',
        'wizard/account_move_reversal_view.xml',
    ],

    'installable': True,

    'auto_install': False,

    'application': True,

    'description': 'Tipos de comprobantes para contabilidad',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
