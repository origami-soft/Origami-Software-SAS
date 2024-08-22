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

    'name': 'l10n ar reject checks move',

    'version': '1.0',

    'summary': 'Asientos de rechazo de cheques propios y de terceros',

    'description': """
Cheques
==================================
    Asientos de rechazo de cheques propios y de terceros
    """,

    'author': 'BLUEORANGE GROUP S.R.L.',

    "website": "https://www.blueorange.com.ar",

    'category': 'Accounting',

    'depends': [
        'l10n_deposit_slip',
        'l10n_reject_checks',
        'l10n_ar_account_check_sale',
        'l10n_ar_account_check_collect',
    ],

    'data': [
        'views/account_third_check_view.xml',
        'views/account_own_check_view.xml',
        'wizard/reject_checks_wizard.xml',
    ],

    'active': False,

    'installable': True,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
