#!/usr/bin/env python
# coding: utf-8

def migrate(cr, installed_version):
    cr.execute("alter table account_third_check add old_dest_payment int")
    cr.execute("select id from account_third_check")
    ids_dict_list = cr.dictfetchall()
    for id_dict in ids_dict_list:
        check_id = id_dict['id']
        cr.execute("select payment_id from third_check_account_payment_rel where third_check_id = {}".format(check_id))
        payment_id_dict = cr.dictfetchone()
        payment_id = payment_id_dict.get('payment_id', "NULL") if payment_id_dict else "NULL"
        cr.execute("update account_third_check set old_dest_payment = {} where id = {}".format(payment_id, check_id))
