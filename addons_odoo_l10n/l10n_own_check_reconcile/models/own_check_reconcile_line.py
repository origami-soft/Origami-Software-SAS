# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class OwnCheckReconcileLine(models.Model):
    _name = 'own.check.reconcile.line'
    _description = 'Línea de conciliación de cheque propio'

    reconcile_id = fields.Many2one(
        comodel_name='own.check.reconcile',
        string="Conciliación",
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
        self.update({
            'amount': self.check_id.amount,
            'check_account_id': self.check_id.journal_id.default_debit_account_id.id,
            'currency_id': self.check_id.currency_id.id,
            'account_id': self.reconcile_id.general_account_id.id})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
