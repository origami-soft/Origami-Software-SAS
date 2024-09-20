#!/usr/bin/env python
# coding: utf-8

from odoo import api, SUPERUSER_ID


def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for tmpl in env['mail.template'].search([('model', '=', 'account.move')]):
        tmpl.write({
            'body_html': tmpl.body_html.replace('object.name', 'object.full_voucher_name'),
            'subject': tmpl.subject.replace('object.name', 'object.full_voucher_name') if tmpl.subject else False,
        })
        for lang in env['res.lang'].search([]):
            tmpl.with_context(lang=lang.code).write({
                'body_html': tmpl.body_html.replace('object.name', 'object.full_voucher_name'),
                'subject': tmpl.subject.replace('object.name', 'object.full_voucher_name') if tmpl.subject else False,
            })
