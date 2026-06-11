# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class AccountPaymentRegister(models.TransientModel):

    _inherit = 'account.payment.register'

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

    @api.onchange('currency_rate')
    def onchange_currency_rate(self):
        for field in self.env['account.payment'].get_payment_line_fields():
            for line in getattr(self, field).filtered(lambda x: x.currency_id == x.payment_id.company_id.currency_id):
                line.rate = self.currency_rate or self.current_currency_rate
                line.onchange_amount()

    @api.depends('currency_id', 'payment_date', 'company_id')
    def compute_current_currency_rate(self):
        """ Calculo la cotizacion actual de la moneda siempre y cuando sea distinta a la de la compañia """
        for payment in self:
            date = payment.payment_date or fields.Date.today()
            company = payment.company_id or self.env.company
            payment.current_currency_rate = self.env['res.currency']._get_conversion_rate(
                payment.currency_id,
                company.currency_id,
                company,
                date
            )

    def _create_payment_vals_from_wizard(self, batch_result):
        res = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard(batch_result)
        res['currency_rate'] = self.currency_rate
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
