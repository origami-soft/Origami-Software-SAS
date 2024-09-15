# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountCheckCollectWizard(models.TransientModel):
    _name = "account.check.collect.wizard"
    _description = 'Wizard de cobro de cheques'

    name = fields.Char(
        'Número'
    )
    bank_id = fields.Many2one(
        'res.bank',
        'Banco'
    )
    bank_journal_id = fields.Many2one(
        'account.journal',
        'Banco',
        domain="[('company_id', '=', company_id), ('type', '=', 'bank'), ('bank_id', '!=', False)]",
    )
    check_type = fields.Selection(
        [('common', 'Común'),
         ('postdated', 'Diferido')],
        string="Tipo",
        default='postdated'
    )
    payment_date = fields.Date(
        string='Fecha de pago',
        required=True
    )
    issue_date = fields.Date(
        string='Fecha de emisión',
        required=True
    )
    amount = fields.Float(
        string='Monto',
        required=True
    )
    check_journal_id = fields.Many2one(
        comodel_name='account.journal',
        domain="[('company_id', '=', company_id), ('payment_usage', '=', 'own_check')]",
        default=lambda self: self.env.company.account_own_check_journal_id,
        string="Diario"
    )
    check_location_id = fields.Many2one(
        comodel_name='account.check.location',
        string='Ubicación'
    )
    collect_date = fields.Date(
        string='Fecha de cobro',
        required=True,
        default=fields.Date.context_today
    )
    journal_id = fields.Many2one(
        'account.journal',
        domain="[('company_id', '=', company_id),('type', 'in', ['bank', 'cash'])]",
        string="Diario",
        required=True
    )
    company_id = fields.Many2one(
        comodel_name='res.company', 
        string="Compañía", 
        required=True, 
        default=lambda self: self.env.company
    )
    collect_from_check = fields.Boolean(
        string="Cobro desde cheque"
    )

    @api.onchange('bank_journal_id')
    def onchange_bank_journal_set_bank(self):
        self.bank_id = self.bank_journal_id.bank_id

    @api.onchange('check_type', 'issue_date')
    def onchange_payment_type(self):
        if self.check_type == 'common' and self.issue_date:
            self.payment_date = self.issue_date

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.update({'journal_id': False,
                     'check_journal_id': self.company_id.account_own_check_journal_id,})

    def get_check_vals(self):
        return {
            'name': self.name,
            'bank_id': self.bank_id.id,
            'bank_journal_id': self.bank_journal_id.id,
            'check_type': self.check_type,
            'payment_date': self.payment_date,
            'collect_date': self.collect_date,
            'issue_date': self.issue_date,
            'amount': self.amount,
            'journal_id': self.check_journal_id.id,
            'check_location_id': self.check_location_id.id,
        }

    def get_move_vals(self, ref):
        return {
            'ref': ref,
            'date': self.collect_date
        }
    
    def get_move_line_vals(self, account, ref, currency=False, debit=0.0, credit=0.0, amount_currency=0.0):
        vals = {
            'account_id': account.id,
            'credit': credit,
            'debit': debit,
            'amount_currency': amount_currency,
            'name': ref,
        }
        if currency:
            vals['currency_id'] = currency.id
        return vals
    
    def _create_collect_check(self):
        check_proxy = self.env['account.own.check']
        return check_proxy.create(self.get_check_vals())

    def _create_collect_move(self, ref):
        debit_account = self.journal_id._get_journal_inbound_outstanding_payment_accounts()[0]
        credit_account = self.company_id.transfer_account_id
        journal = self.journal_id
        return self._create_move(ref, journal, debit_account, credit_account)
        
    def _create_check_collect_move(self, check, ref):
        debit_account = self.company_id.transfer_account_id
        credit_account = check.journal_id._get_journal_inbound_outstanding_payment_accounts()[0]
        journal = check.journal_id
        return self._create_move(ref, journal, debit_account, credit_account)

    def _create_move(self, ref, journal, debit_account, credit_account):
        move_proxy = self.env['account.move']
        current_currency = self.check_journal_id.currency_id
        company_currency = self.company_id.currency_id

        if current_currency != company_currency:
            converted_amount = current_currency._convert(
                self.amount,
                company_currency,
                self.company_id,
                self.issue_date
            )
            move_credit_vals = self.get_move_line_vals(credit_account, ref, current_currency, credit=converted_amount, amount_currency=-self.amount)
            move_debit_vals = self.get_move_line_vals(debit_account, ref, current_currency, debit=converted_amount, amount_currency=self.amount)
        else:
            converted_amount = self.amount
            move_credit_vals = self.get_move_line_vals(credit_account, ref, credit=converted_amount)
            move_debit_vals = self.get_move_line_vals(debit_account, ref, debit=converted_amount)

        move_vals = self.get_move_vals(ref)
        move_vals['line_ids'] = [
            (0, 0, move_credit_vals),
            (0, 0, move_debit_vals),
        ]

        move = move_proxy.with_context(default_journal_id=journal.id).create(move_vals)
        return move

    def get_collect_vals(self, move, check_move):
        vals = {
            'collect_move_id': move.id,
            'collect_check_move_id': check_move.id,
            'payment_date': self.payment_date,
            'collect_date': self.collect_date,
            'issue_date': self.issue_date,
            'amount': self.amount
        }
        return vals

    def collect_check(self):
        self.ensure_one()
        check = self._create_collect_check() if not self.collect_from_check else self.env['account.own.check'].browse(self.env.context.get('active_id'))
        ref = 'Cobro de cheque {check}'.format(check=check.display_name)
        check_move = self.with_company(self.company_id)._create_check_collect_move(check, ref)
        move = self.with_company(self.company_id)._create_collect_move(ref)
        check_move.action_post()
        move.action_post()
        collect_vals = self.get_collect_vals(move, check_move)
        check.post_collect(collect_vals)
        if not self.collect_from_check:
            return check._get_own_check_view()
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
