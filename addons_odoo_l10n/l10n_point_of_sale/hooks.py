# -*- encoding: utf-8 -*-

def post_init_hook(env):
    for tmpl in env['mail.template'].search([('model', '=', 'account.move')]):
        tmpl.write({
            'body_html': tmpl.body_html.replace('object.name', 'object.full_voucher_name') if tmpl.body_html else False,
            'subject': tmpl.subject.replace('object.name', 'object.full_voucher_name') if tmpl.subject else False,
        })
        for lang in env['res.lang'].search([]):
            tmpl.with_context(lang=lang.code).write({
                'body_html': tmpl.body_html.replace('object.name', 'object.full_voucher_name') if tmpl.body_html else False,
                'subject': tmpl.subject.replace('object.name', 'object.full_voucher_name') if tmpl.subject else False,
            })

def uninstall_hook(env):
    for tmpl in env['mail.template'].search([('model', '=', 'account.move')]):
        tmpl.write({
            'body_html': tmpl.body_html.replace('object.full_voucher_name', 'object.name') if tmpl.body_html else False,
            'subject': tmpl.subject.replace('object.full_voucher_name', 'object.name') if tmpl.subject else False,
        })
        for lang in env['res.lang'].search([]):
            tmpl.with_context(lang=lang.code).write({
                'body_html': tmpl.body_html.replace('object.full_voucher_name', 'object.name') if tmpl.body_html else False,
                'subject': tmpl.subject.replace('object.full_voucher_name', 'object.name') if tmpl.subject else False,
            })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: