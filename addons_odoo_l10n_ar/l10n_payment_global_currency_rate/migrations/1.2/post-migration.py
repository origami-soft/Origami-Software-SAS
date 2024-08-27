#!/usr/bin/env python
# coding: utf-8

from odoo import api, SUPERUSER_ID


def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    payments = env['account.payment'].search([('communication', '!=', False)])
    payments = payments.filtered(lambda l: l.communication.startswith("('"))
    moves = payments.mapped('move_line_ids.move_id').filtered(lambda l: l.ref and l.ref.startswith("('"))
    for p in payments:
        p.communication = p.communication.replace("('", "").replace("',)", "")
    for m in moves:
        m.ref = m.ref.replace("('", "").replace("',)", "")

