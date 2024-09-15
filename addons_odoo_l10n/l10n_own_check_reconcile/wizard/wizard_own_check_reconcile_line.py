# -*git- encoding: utf-8 -*-

from odoo import models, fields, api


class WizardOwnCheckReconcileLine(models.TransientModel):
    _name = 'wizard.own.check.reconcile.line'
    _description = 'Línea de registro de débito de cheque propio'

    reconcile_id = fields.Many2one(
        comodel_name='wizard.own.check.reconcile',
        string="Registro de débito",
    )

    check_id = fields.Many2one(
        comodel_name='account.own.check',
        string="Cheque",
        required=True,
        check_company=True
    )

    check_account_id = fields.Many2one(
        comodel_name='account.account',
        string="Contrapartida",
    )

    account_id = fields.Many2one(
        comodel_name='account.account',
        string="Cuenta",
        check_company=True
    )

    amount = fields.Float(
        string="Monto",
    )

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string="Moneda"
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañía',
        readonly=True
    )

    @api.onchange('check_id')
    def onchange_check(self):
        if self.check_id:
            self.update({
                'amount': self.check_id.amount,
                'check_account_id': self.check_id.journal_id._get_journal_outbound_outstanding_payment_accounts()[0].id,
                'account_id': self.check_id.bank_journal_id._get_journal_outbound_outstanding_payment_accounts()[0].id,
                'currency_id': self.check_id.currency_id.id
            })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
