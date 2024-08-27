# -*- encoding: utf-8 -*-
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

    'name': 'l10n_ar_vat_diary',

    'version': '2.2.1',

    'category': 'Accounting',

    'summary': 'Libro de IVA para Argentina',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'depends': [
        'l10n_ar_retentions',
    ],

    'data': [
        'views/account_fiscal_position.xml',
        'views/account_tax.xml',
        'views/vat_diary.xml',
        'report/vat_diary_pdf_report_data.xml',
        'report/vat_diary_pdf_report.xml',
        'security/rule.xml',
        'security/ir.model.access.csv'
    ],

    'installable': True,

    'auto_install': False,

    'application': True,

    'description': 'Libro de IVA para Argentina',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
