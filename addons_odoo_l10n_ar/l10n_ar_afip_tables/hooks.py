# -*- encoding: utf-8 -*-

def post_init_hook(env):
    for c in env['res.company'].search([]):
        c.create_tax_codes_models()

def uninstall_hook(env):
    env['res.company'].search([]).delete_tax_codes_models()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
