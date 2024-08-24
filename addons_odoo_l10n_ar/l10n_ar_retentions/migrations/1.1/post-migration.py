#!/usr/bin/env python
# coding: utf-8

from odoo import api, SUPERUSER_ID


def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.ref('l10n_ar_retentions.account_payment_retention_multi').write({'domain_force': "[('company_id','in', company_ids)]"})
