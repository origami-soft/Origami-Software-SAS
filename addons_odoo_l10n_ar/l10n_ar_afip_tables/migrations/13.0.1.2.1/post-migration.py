#!/usr/bin/env python
# coding: utf-8

from odoo import api, SUPERUSER_ID


def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    fpos_ivari = env['ir.model.data'].xmlid_to_object(
        'l10n_ar_afip_tables.account_fiscal_position_ivari', raise_if_not_found=False
    )
    fpos_mon = env['ir.model.data'].xmlid_to_object(
        'l10n_ar_afip_tables.account_fiscal_position_mon', raise_if_not_found=False
    )
    denomination_a = env['ir.model.data'].xmlid_to_object(
        'l10n_ar_afip_tables.account_denomination_a', raise_if_not_found=False
    )
    if fpos_ivari and fpos_mon and denomination_a:
        fpos_ivari.denomination_fiscal_position_ids.filtered(
            lambda x: x.receipt_fiscal_position_id == fpos_mon
        ).write({'account_denomination_id': denomination_a.id})
