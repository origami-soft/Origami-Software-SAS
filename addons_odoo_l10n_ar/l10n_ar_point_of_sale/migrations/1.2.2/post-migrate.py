# -*- coding: utf-8 -*-

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    cr.execute(
        "CREATE INDEX IF NOT EXISTS account_move_voucher_name_index ON account_move (voucher_name)"
    )
