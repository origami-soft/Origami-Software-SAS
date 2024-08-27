#!/usr/bin/env python
# coding: utf-8

from odoo import api, SUPERUSER_ID


def migrate(cr, installed_version):
    cr.execute("update stock_move set reference = p.name from stock_picking p where picking_id = p.id and p.cai is not null")
