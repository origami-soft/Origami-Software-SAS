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

    'name': 'Payment imputation default journal',

    'version': '1.0',

    'category': 'Accounting',

    'summary': 'Diarios de pagos por default en imputaciones de pagos',

    'author': 'BLUEORANGE GROUP S.R.L. / NEXIT',

    'website': 'https://www.blueorange.com.ar',

    'depends': [
        'payment_imputation',
        'l10n_default_payment_journal'
    ],

    'data': [

    ],

    'installable': True,

    'auto_install': True,

    'application': True,

    'description': 'Diarios de pagos por default en imputaciones de pagos',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
