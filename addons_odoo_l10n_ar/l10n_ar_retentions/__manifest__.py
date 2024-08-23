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

    'name': 'l10n_ar_retentions',

    'version': '1.3.0',

    'category': 'Accounting',

    'summary': 'Retenciones para Argentina',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'http://www.blueorange.com.ar',

    'depends': [
        'l10n_payment_line',
        'l10n_ar_taxes',
        'payment_imputation',
    ],

    'data': [
        'views/account_payment_retention.xml',
        'views/account_payment.xml',
        'views/res_config_settings.xml',
        'views/retention_activity.xml',
        'views/retention_retention.xml',
        'data/retention_activities.xml',
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'data/security.xml',
    ],

    'installable': True,

    'auto_install': False,

    'application': True,

    'description': 'Contempla retenciones en la carga de pagos',

}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
