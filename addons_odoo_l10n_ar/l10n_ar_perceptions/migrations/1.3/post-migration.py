#!/usr/bin/env python
# coding: utf-8

from odoo import api, SUPERUSER_ID


def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    cr.execute("select array_agg(distinct move_id) from account_move_line where abs(price_total) > abs(2 * price_subtotal) and display_type = 'product' and write_date >= '2026-01-01'")
    move_ids = cr.fetchone()[0]
    if move_ids:
        moves = env['account.move'].browse(move_ids)
        moves.mapped('line_ids')._compute_totals()
