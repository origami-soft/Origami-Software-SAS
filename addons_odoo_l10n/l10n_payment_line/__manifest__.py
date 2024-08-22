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

    'name': 'l10n Payment Line',

    'version': '1.2.2',

    'category': '',

    'summary': 'l10n Payment Line',

    'author': 'BLUEORANGE GROUP S.R.L. / NEXIT',

    'website': 'https://www.blueorange.com.ar',

    'depends': [

        'account',
        'l10n_fixed_rate',

    ],

    'data': [

        'views/account_journal.xml',
        'views/account_payment.xml',
        'views/res_config_settings.xml',

    ],

    'installable': True,

    'auto_install': False,

    'application': True,

    'description': 'Abstracción para líneas de pago',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
