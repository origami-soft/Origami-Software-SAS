#!/usr/bin/env python
# coding: utf-8


def migrate(cr, installed_version):
    cr.execute("alter table account_own_check drop constraint if exists account_own_check_name_uniq")
