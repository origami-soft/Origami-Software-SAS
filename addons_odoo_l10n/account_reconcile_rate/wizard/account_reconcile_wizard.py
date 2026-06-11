# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountReconcileWizard(models.TransientModel):
    _inherit = 'account.reconcile.wizard'

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        move_lines = self.env['account.move.line'].browse(self.env.context.get('active_ids'))
        move_lines = move_lines.filtered(lambda l: l.move_id.move_type != 'entry')
        amount_curr = sum(move_lines.mapped('amount_currency'))
        res['rate'] = sum(move_lines.mapped('balance')) / amount_curr if amount_curr else 0
        return res

    rate = fields.Float("Cotización", digits=(12, 6))

    @api.depends('move_line_ids', 'rate')
    def _compute_reco_wizard_data(self):
        res = super()._compute_reco_wizard_data()
        for r in self.filtered(lambda l: l.reco_currency_id != l.company_currency_id and l.rate):
            r.amount = r.amount_currency * r.rate
        return res

    def reconcile(self):
        self = self.with_context({
            'no_exchange_difference': True,
            'fixed_rate': self.rate,
            'fixed_from_currency': self.reco_currency_id,
            'fixed_to_currency': self.company_currency_id,
        })
        return super().reconcile()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
