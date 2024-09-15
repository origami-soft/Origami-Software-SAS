# -*- encoding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import ValidationError


class WizardDepositSlip(models.TransientModel):
    _name = "wizard.deposit.slip"
    _description = 'Wizard de boleta de depósito'

    def get_valid_deposit(self):
        return all(r.state == 'wallet' for r in self._get_checks())

    def _get_checks(self):
        checks = self.env['account.third.check'].browse(
            self.env.context.get('active_ids') or self.env.context.get('active_id'))
        return checks

    def get_total(self):
        return sum(check.amount for check in self._get_checks())

    def get_currency(self):
        checks = self._get_checks()
        if checks:
            currency = checks.mapped('currency_id')
            if len(currency) > 1:
                raise ValidationError("No se pueden depositar cheques de distintas monedas"
                                      " en la misma boleta de deposito")
            return currency.id

    journal_id = fields.Many2one(
        'account.journal',
        'Cuenta bancaria',
        domain=[('type', '=', 'bank')],
        required=True
    )
    date = fields.Date(
        'Fecha',
        default=fields.Date.context_today,
        required=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        'Moneda',
        required=True,
        default=get_currency
    )
    total = fields.Monetary(
        'Total',
        default=get_total
    )
    valid_deposit = fields.Boolean(
        default=get_valid_deposit
    )

    def action_create_deposit_slip(self):
        """
        Crea la boleta de depósito y relaciona los cheques a la misma
        :return: Formulario de la boleta de depósito creada
        """
        deposit_slip = self._create_deposit_slip()

        return {
            'name': 'Boleta de deposito',
            'views': [[False, "form"]],
            'res_model': 'account.deposit.slip',
            'type': 'ir.actions.act_window',
            'res_id': deposit_slip.id,
        }
    
    def _get_deposit_slip_vals(self):
        self.ensure_one()
        return {
            'date': self.date,
            'journal_id': self.journal_id.id,
            'amount': self.total,
            'check_ids': [(6, 0, self._get_checks().ids)],
            'state': 'draft',
            'currency_id': self.currency_id.id,
        }

    def _create_deposit_slip(self):
        """
        Crea la boleta de depósito y la asocia al asiento
        :param name: Nombre de de la boleta de deposito
        :param move: Asiento asociado a la boleta de deposito
        :return: account.deposit.slip - Boleta de deposito creada
        """
        return self.env['account.deposit.slip'].create(self._get_deposit_slip_vals())

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
