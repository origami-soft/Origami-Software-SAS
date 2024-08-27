#!/usr/bin/env python
# coding: utf-8

from odoo import api, SUPERUSER_ID


def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    denom_fpos = env['ir.model.data'].xmlid_to_object(
        'l10n_ar_afip_tables.fpos_ivari_to_ivari_m', raise_if_not_found=False
    )
    fpos_ivari_m = env['ir.model.data'].xmlid_to_object(
        'l10n_ar_afip_tables.account_fiscal_position_ivari_m', raise_if_not_found=False
    )
    if denom_fpos and fpos_ivari_m:
        denom_fpos.write({'receipt_fiscal_position_id': fpos_ivari_m.id})
