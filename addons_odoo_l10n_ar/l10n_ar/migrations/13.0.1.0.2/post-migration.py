#!/usr/bin/env python
# coding: utf-8

from odoo import api, SUPERUSER_ID


def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    tax_model = 'account.tax'
    tax_ids = env['ir.model.data'].search([('name', 'like', 'tax_percepcion_iibb_caba_efectuada'), ('model', '=', tax_model)]).mapped('res_id')
    env[tax_model].browse(tax_ids).write({'amount_type': 'perception'})
    perception_model = 'perception.perception'
    perception_ids = env['ir.model.data'].search([('name', 'like', 'perception_perception_iibb_pba_sufrida'), ('model', '=', perception_model)]).mapped('res_id')
    env[perception_model].browse(perception_ids).write({'state_id': env.ref('base.state_ar_b').id})
