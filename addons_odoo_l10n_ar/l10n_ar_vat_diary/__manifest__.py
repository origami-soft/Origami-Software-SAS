# -*- encoding: utf-8 -*-

{

    'name': 'l10n_ar_vat_diary',

    'version': '1.0.3',

    'category': 'Accounting',

    'summary': 'Libro de IVA para Argentina',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'depends': [
        'l10n_ar_retentions',
        'l10n_ar_perceptions',
    ],

    'data': [
        'views/account_fiscal_position.xml',
        'views/account_tax.xml',
        'views/vat_diary.xml',
        'report/vat_diary_pdf_report_data.xml',
        'report/vat_diary_pdf_report.xml',
        'security/ir.model.access.csv'
    ],

    'installable': True,

    'auto_install': False,

    'application': False,

    'description': 'Libro de IVA para Argentina',

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
