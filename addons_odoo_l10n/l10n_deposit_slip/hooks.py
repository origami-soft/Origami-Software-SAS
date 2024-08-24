# -*- encoding: utf-8 -*-

def post_init_hook(env):
    env['res.company'].search([]).create_missing_deposit_slip_sequences()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
