# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    show_payment_lines = fields.Boolean(compute='_compute_show_payment_lines')
    payment_usage = fields.Selection(related='journal_id.payment_usage')
    difference = fields.Float(string="Diferencia")

    def _get_payment_line_recordsets(self):
        return [getattr(self, field) for field in self.env['account.payment'].get_payment_line_fields()]

    def recalculate_difference(self):
        total = 0
        for recordset in self._get_payment_line_recordsets():
            total += sum(getattr(r, r.get_amount_field(self)) for r in recordset)
        self.difference = self.amount - round(total, 2)
    
    @api.onchange('amount')
    def onchange_amount_recalculate_difference(self):
        self.recalculate_difference()

    @api.depends('journal_id')
    def _compute_show_payment_lines(self):
        self.show_payment_lines = self.payment_usage == 'document_book'
    
    @api.model
    def _get_batch_journal(self, batch_result):
        """
        Piso el método para filtrar los diarios que sean seleccionables en la cabecera de pagos
        Línea agregada: 62
        """
        payment_values = batch_result['payment_values']
        foreign_currency_id = payment_values['currency_id']
        partner_bank_id = payment_values['partner_bank_id']

        currency_domain = [('currency_id', '=', foreign_currency_id)]
        partner_bank_domain = [('bank_account_id', '=', partner_bank_id)]

        default_domain = [
            ('type', 'in', ('bank', 'cash')),
            ('company_id', '=', batch_result['lines'].company_id.id),
            ('selectable_in_payments', '=', True),
        ]

        if partner_bank_id:
            extra_domains = (
                currency_domain + partner_bank_domain,
                partner_bank_domain,
                currency_domain,
                [],
            )
        else:
            extra_domains = (
                currency_domain,
                [],
            )

        for extra_domain in extra_domains:
            journal = self.env['account.journal'].search(default_domain + extra_domain, limit=1)
            if journal:
                return journal

        return self.env['account.journal']
    
    @api.depends('available_journal_ids')
    def _compute_journal_id(self):
        """
        Piso el método para filtrar los diarios que sean seleccionables en la cabecera de pagos
        """
        for wizard in self:
            if wizard.can_edit_wizard:
                batch = wizard._get_batches()[0]
                wizard.journal_id = wizard._get_batch_journal(batch)
            else:
                wizard.journal_id = self.env['account.journal'].search([
                    *self.env['account.journal']._check_company_domain(wizard.company_id),
                    ('type', 'in', ('bank', 'cash')),
                    ('id', 'in', self.available_journal_ids.ids),
                    ('selectable_in_payments', '=', True),
                ], limit=1)

    @api.depends('payment_method_line_id', 'journal_id.payment_usage')
    def _compute_show_require_partner_bank(self):
        res = super(AccountPaymentRegister, self)._compute_show_require_partner_bank()
        for payment in self:
            payment.show_partner_bank_account = payment.show_partner_bank_account and payment.journal_id.payment_usage != 'document_book'
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
