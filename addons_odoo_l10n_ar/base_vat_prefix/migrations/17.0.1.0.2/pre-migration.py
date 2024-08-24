#!/usr/bin/env python
# coding: utf-8


# from odoo import api, SUPERUSER_ID
#
#
# def migrate(cr, version):
#     env = api.Environment(cr, SUPERUSER_ID, {})
#
#     cr.execute("""
#         DELETE FROM res_country WHERE code IS NULL OR code = 'f' OR code = '';
#     """)
#
#     cr.commit()
