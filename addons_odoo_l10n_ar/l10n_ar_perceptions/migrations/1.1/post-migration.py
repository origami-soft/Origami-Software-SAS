#!/usr/bin/env python
# coding: utf-8

from odoo import api, SUPERUSER_ID


def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for tax in env['perception.perception'].search([]).mapped('tax_id'):
        tax.amount_type = 'perception'
        tax.invoice_repartition_line_ids.filtered(lambda l: l.account_id).write({'factor_percent': 100})
        tax.refund_repartition_line_ids.filtered(lambda l: l.account_id).write({'factor_percent': 100})
