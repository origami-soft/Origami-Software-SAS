# -*- encoding: utf-8 -*-

from odoo import models, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    def get_deposit_slip_sequence_vals(self):
        self.ensure_one()
        return {
            'name': "Boleta de depósito",
            'code': 'account.deposit.slip.sequence',
            'prefix': 'BOD/',
            'padding': 5,
            'number_increment': 1,
            'implementation': 'no_gap',
            'company_id': self.id,
        }

    def create_deposit_slip_sequence(self):
        return self.env['ir.sequence'].create(self.get_deposit_slip_sequence_vals())

    def create_missing_deposit_slip_sequences(self):
        companies_with_seq = self.env['ir.sequence'].search([('code', '=', 'account.deposit.slip.sequence')]).mapped('company_id')
        for r in self.filtered(lambda l: l not in companies_with_seq):
            r.create_deposit_slip_sequence()

    @api.model
    def create(self, vals):
        res = super(ResCompany, self).create(vals)
        res.create_deposit_slip_sequence()
        return res

    def unlink(self):
        self.env['ir.sequence'].search([('code', '=', 'account.deposit.slip.sequence'), ('company_id', 'in', self.ids)]).unlink()
        return super(ResCompany, self).unlink()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
