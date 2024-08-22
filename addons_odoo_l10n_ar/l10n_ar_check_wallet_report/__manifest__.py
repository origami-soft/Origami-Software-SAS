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

    'name': 'l10n_ar_check_wallet_report',

    'version': '1.0.3',

    'category': 'Localization',

    'summary': 'Reporte de cheques en cartera',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'license': 'AGPL-3',

    'depends': [

        'l10n_deposit_slip',
        'l10n_ar_account_check_sale',
        'l10n_reject_checks',
        
    ],

    'data': [

        'wizard/check_wallet_report_wizard.xml',

    ],

    'installable': True,

    'auto_install': False,

    'application': False,

    'description': """Reporte de cheques en cartera""",

}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
