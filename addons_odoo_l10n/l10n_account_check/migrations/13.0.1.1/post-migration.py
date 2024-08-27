#!/usr/bin/env python
# coding: utf-8

def migrate(cr, installed_version):
    cr.execute("update account_third_check set destination_payment_id = old_dest_payment")
    cr.execute("alter table account_third_check drop column old_dest_payment")
