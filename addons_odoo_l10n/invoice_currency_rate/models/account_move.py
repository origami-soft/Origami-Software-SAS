# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):

    _inherit = 'account.move'

    currency_rate = fields.Float(
        string='Cotización a utilizar',
        digits=(12, 6),
    )
    current_currency_rate = fields.Float(
        string='Cotización actual',
        compute='compute_current_currency_rate',
        digits=(12, 6),
    )
    need_rate = fields.Boolean(
        string='Necesita cotización',
        related='currency_id.need_rate'
    )

    @api.onchange('currency_rate')
    def onchange_currency_rate(self):
        self._compute_amount()

    @api.onchange('currency_id')
    def onchange_currency_currency_rate(self):
        self.currency_rate = self.current_currency_rate if self.need_rate else 0

    @api.depends('currency_id', 'company_currency_id', 'invoice_date')
    def compute_current_currency_rate(self):
        """ Calculo la cotizacion actual de la moneda siempre y cuando sea distinta a la de la compañia """
        for invoice in self:
            if invoice.currency_id and invoice.currency_id != invoice.company_id.currency_id:
                date = invoice.invoice_date or fields.Date.today()
                rate = self.env['res.currency']._get_conversion_rate(invoice.currency_id, invoice.company_id.currency_id, invoice.company_id, date)
                invoice.current_currency_rate = rate
            else:
                invoice.current_currency_rate = 1

    def _recompute_dynamic_lines(self, recompute_all_taxes=False, recompute_tax_base_amount=False):
        if self.need_rate:
            if not self.currency_rate:
                self.currency_rate = self.current_currency_rate
            self = self.with_context(
                fixed_rate=self.currency_rate,
                fixed_from_currency=self.currency_id,
                fixed_to_currency=self.company_id.currency_id
            )
        return super(AccountMove, self)._recompute_dynamic_lines(recompute_all_taxes, recompute_tax_base_amount)

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for invoice in res:
            if invoice.need_rate and not invoice.currency_rate:
                invoice.currency_rate = invoice.current_currency_rate
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
