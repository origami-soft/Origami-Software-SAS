#!/usr/bin/env python
# coding: utf-8


def migrate(cr, installed_version):
    cr.execute("""
        update account_move
        set deposit_slip_id = account_deposit_slip.id
        from account_deposit_slip
        where account_deposit_slip.move_id = account_move.id
    """)
