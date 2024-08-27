# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{

    'name': 'base_vat_ar',

    'version': '1.0',

    'summary': 'Document type and validation for partners for Argentina',

    'description': 'Document type and validation for partners for Argentina',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'license': 'OPL-1',

    'category': 'base',

    'depends': [
        'partner_document_type'
    ],

    'data': [
        'views/res_country_view.xml',
        'data/res_country_data.xml',
        'data/res.country.csv',
    ],

    'active': False,

    'installable': True,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
