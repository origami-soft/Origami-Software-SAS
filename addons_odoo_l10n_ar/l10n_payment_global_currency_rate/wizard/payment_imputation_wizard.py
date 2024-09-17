# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class PaymentImputationWizard(models.TransientModel):

    _inherit = 'payment.imputation.wizard'

    currency_rate = fields.Float(
        string='Cotización a utilizar',
    )
    current_currency_rate = fields.Float(
        string='Cotización actual',
        compute='compute_current_currency_rate'
    )
    need_rate = fields.Boolean(
        string='Necesita cotización',
        related='currency_id.need_rate'
    )

    @api.onchange('need_rate')
    def onchange_need_rate(self):
        self.update({
            'currency_rate': 0,
        })

    @api.depends('currency_id', 'company_id.currency_id', 'date')
    def compute_current_currency_rate(self):
        if self.currency_id:
            self.current_currency_rate = self.env['res.currency']._get_conversion_rate(
                self.currency_id,
                self.company_id.currency_id or self.env.company.currency_id,
                self.company_id or self.env.company,
                self.date or fields.Date.today()
            )

    def _get_payment_vals(self):
        vals = super(PaymentImputationWizard, self)._get_payment_vals()
        vals['currency_rate'] = self.currency_rate
        vals['ref'] = ', '.join(self._get_imputations_ref())
        return vals

    def _get_imputations_ref(self):
        imputations_ref = []
        for imputation in self.debit_imputation_line_ids.filtered(lambda x: x.amount and x.move_line_id.move_id):
            imputations_ref.append(imputation.move_line_id.full_voucher_name)
        return imputations_ref

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
