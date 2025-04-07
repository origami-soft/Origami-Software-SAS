#!/usr/bin/env python
# coding: utf-8

from odoo import api, SUPERUSER_ID


def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['account.fiscal.position'].search([
        ('ar_fiscal_position_id', '=', env.ref('l10n_ar.ar_fiscal_position_ivari').id)
    ]).write({'auto_apply': False})
