# -*- coding: utf-8 -*-
{
    "name": "L10n_ar_restrict_state",
    "version": "1.0",
    "summary": """ Configuración para evitar que puedan ser devueltas a borrador las facturas publicadas con CAE """,
    "description": """ Configuración para evitar que puedan ser devueltas a borrador las facturas publicadas con CAE """,
    "author": "BLUEORANGE GROUP S.R.L.",
    "website": "https://www.blueorange.com.ar",
    "category": "",
    "depends": ["l10n_ar_config_settings", "account"],
    "data": [
        "views/res_config_settings_views.xml"
    ],
    
    "application": True,
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
