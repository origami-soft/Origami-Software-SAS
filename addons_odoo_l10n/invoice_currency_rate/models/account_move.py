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
            invoice.current_currency_rate = self._get_currency_rate(
                invoice.currency_id,
                invoice.company_id,
                invoice.invoice_date or fields.Date.today()
            )

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

    def _get_currency_rate(self, currency, company, date):
        """ Helper method to get the currency rate """
        if currency and currency != company.currency_id:
            rate = self.env['res.currency']._get_conversion_rate(
                currency, company.currency_id, company, date)
            return round(rate, 6)
        return 1

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            currency_id = vals.get('currency_id')
            company_id = vals.get('company_id')
            invoice_date = vals.get('invoice_date', fields.Date.today())

            if currency_id and 'currency_rate' not in vals:
                currency = self.env['res.currency'].browse(currency_id)
                company = self.env['res.company'].browse(company_id)
                vals['currency_rate'] = self._get_currency_rate(currency, company, invoice_date)

        # Crea el registro con los valores modificados
        return super(AccountMove, self).create(vals_list)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
