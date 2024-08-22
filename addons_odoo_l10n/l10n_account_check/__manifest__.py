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

    'name': 'l10n account check',

    'version': '1.5.0',

    'summary': 'Cheques propios y de terceros',

    'description': """
Cheques
==================================
    Cheques propios desde pagos.\n
    Cheques de terceros para cobros y pagos.\n
    """,

    'author': 'BLUEORANGE GROUP S.R.L. / NEXIT',

    'website': 'https://www.blueorange.com.ar',

    'category': 'Accounting',

    'depends': [
        'l10n_payment_line',
    ],

    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/account_own_check.xml',
        'views/account_third_check.xml',
        'views/res_config_settings.xml',
        'views/account_payment.xml',
        'views/account_journal.xml',
        'views/menu.xml',
        'wizard/check_correct_wizard.xml',
        'security/security.xml',
    ],

    'active': False,

    'installable': True,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
