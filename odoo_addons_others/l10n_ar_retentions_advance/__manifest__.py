# -*- encoding: utf-8 -*-

{

    "name": "Retentions Advance",

    "summary": """Retenciones""",

    "description": """Retenciones""",

    "author": "BLUEORANGE GROUP S.R.L.",

    "website": "https://www.blueorange.com.ar",

    "category": "Account",

    "version": "1.0",

    "license": 'OPL-1',

    "depends": [
        "l10n_ar_retentions",
    ],

    "data": [
        'security/ir.model.access.csv',
        'views/retention_retention.xml',
        'views/res_partner.xml',
        'views/res_company.xml',
        'data/retention_rules.xml',
    ],

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
