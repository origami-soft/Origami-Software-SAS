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

    'name': 'l10n_ar_all',

    'version': '1.0',

    'summary': 'Localizacion Argentina',

    'description': """
Modulo encargado de instalar todos los modulos requeridos para la localizacion Argentina.
    """,

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'http://www.blueorange.com.ar',

    'category': 'Localization',

    'depends': [
        'base_vat_ar',
        'l10n_ar_account_check_collect',
        'l10n_ar_account_check_sale',
        'l10n_ar_account_payment_report',
        'l10n_ar_afip_import_documents',
        'l10n_ar_check_location',
        'l10n_ar_general_ledger',
        'l10n_ar_electronic_invoice_report',
        'l10n_ar_perceptions',
        'l10n_ar_reject_checks_move',
        'l10n_ar_sale',
        'l10n_ar_stock_picking_report',
        'vat_diary_jurisdiction_name',
        'l10n_credit_cards',
        'l10n_payment_global_currency_rate',
        'l10n_ar_bank_reconcile',
        'l10n_ar_check_wallet_report',
        'currency_rate_update_bna',
    ],

    'data': [

    ],

    'active': False,

    'installable': True,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: