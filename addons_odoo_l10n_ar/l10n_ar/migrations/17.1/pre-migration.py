#!/usr/bin/env python
# coding: utf-8

from odoo.upgrade.util import remove_field, remove_view

def migrate(cr, version):
    # Eliminar vistas obsoletas antes de actualizar la base de datos
    remove_view(cr, "l10n_ar.tax_exempt_form")

    # Eliminar campos obsoletos de la base de datos
    remove_field(cr, 'account.setup.bank.manual.config', 'cbu')
    remove_field(cr, 'res.users', 'iibb_situation')
    remove_field(cr, 'res.users', 'start_date')
    remove_field(cr, 'res.users', 'iibb_number')
    remove_field(cr, 'account.tax.repartition.line', 'amount_type')
