# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    payment_usage = fields.Selection(selection=[('document_book', "Transitorio")], string="Uso en pagos")
    multiple_payment_account_id = fields.Many2one('account.account', "Cuenta para pagos múltiples")
    selectable_in_payments = fields.Boolean("Seleccionable en cabecera de pagos", default=True)

    @api.onchange('type')
    def onchange_type_set_payment_usage(self):
        if self.type not in ('bank', 'cash'):
            self.payment_usage = False

    @api.onchange('payment_usage')
    def onchange_payment_usage(self):
        self.multiple_payment_account_id = False

    @api.onchange('multiple_payment_account_id')
    def onchange_multiple_payment_account(self):
        self.default_account_id = self.multiple_payment_account_id
        self.inbound_payment_method_line_ids.update({'payment_account_id': self.multiple_payment_account_id.id})
        self.outbound_payment_method_line_ids.update({'payment_account_id': self.multiple_payment_account_id.id})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
