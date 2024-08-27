# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

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
        domain="[('company_id', '=', company_id),\
        ('multiple_payment_journal', '=', False), ('check_journal', '=', True)]",
        default= lambda self: self.env.company.account_own_check_journal_id,
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
            'journal_id': self.journal_id.id,
            'date': self.issue_date
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

    def _create_collect_move(self, check, ref):

        move_proxy = self.env['account.move']

        current_currency = self.check_journal_id.currency_id
        company_currency = self.company_id.currency_id

        check_account_id = self.check_journal_id.default_credit_account_id
        account_id = self.journal_id.default_debit_account_id

        if not check_account_id:
            raise ValidationError("El diario del cheque no tiene cuentas contables configuradas.\n"
                                  "Por favor, configurarla en el diario correspondiente.")
        elif not account_id:
            raise ValidationError("El diario del cobro no tiene cuentas contables configuradas.\n"
                                  "Por favor, configurarla en el diario correspondiente.")

        if current_currency != company_currency:
            converted_amount = current_currency._convert(
                self.amount,
                company_currency,
                self.company_id,
                self.issue_date
            )
            move_credit_vals = self.get_move_line_vals(check_account_id, ref, current_currency, credit=converted_amount, amount_currency=-self.amount)

            move_debit_vals = self.get_move_line_vals(account_id, ref, current_currency, debit=converted_amount, amount_currency=self.amount)
        else:
            converted_amount = self.amount
            move_credit_vals = self.get_move_line_vals(check_account_id, ref, credit=converted_amount)

            move_debit_vals = self.get_move_line_vals(account_id, ref, debit=converted_amount)

        move_vals = self.get_move_vals(ref)
        move_vals['line_ids'] = [
            (0, 0, move_credit_vals),
            (0, 0, move_debit_vals),
        ]

        move = move_proxy.create(move_vals)

        return move

    def get_collect_vals(self, move, amount=0.0, payment_date=False, collect_date=False, issue_date=False, collect_from_check=False):
        vals = {
            'collect_move_id': move.id
        }
        if collect_from_check:
            vals.update({
                'amount': amount,
                'payment_date': payment_date,
                'collect_date': collect_date,
                'issue_date': issue_date
            })
        return vals

    def collect_check(self):
        self.ensure_one()
        check = self._create_collect_check() if not self.collect_from_check else self.env['account.own.check'].browse(self.env.context.get('active_id'))
        ref = 'Cobro de cheque {check}'.format(check=check.display_name)
        move = self.with_context(force_company=self.company_id.id)._create_collect_move(check, ref)
        move.post()
        collect_vals = self.get_collect_vals(move) if not self.collect_from_check else self.get_collect_vals(move, amount=self.amount,
                                                                                                            payment_date=self.payment_date,
                                                                                                            collect_date=self.collect_date,
                                                                                                            issue_date=self.issue_date,
                                                                                                            collect_from_check=True)
        check.post_collect(collect_vals)
        if not self.collect_from_check:
            return check._get_own_check_view()
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
