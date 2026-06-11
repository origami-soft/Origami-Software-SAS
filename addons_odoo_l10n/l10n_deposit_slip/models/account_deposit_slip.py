# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from ..exceptions import exceptions


class AccountDepositSlip(models.Model):

    _name = "account.deposit.slip"
    _description = 'Boleta de depósito'
    _inherit = ['mail.thread']

    @api.depends('check_ids')
    def _get_checks_total(self):
        for each in self:
            each.amount = sum(check.amount for check in each.check_ids)

    name = fields.Char(
        string='Boleta de depósito',
        readonly=True,
        tracking=True
    )
    reference = fields.Char(
        string='Referencia',
        tracking=True
    )
    date = fields.Date(
        'Fecha',
        required=True,
        tracking=True
    )
    journal_id = fields.Many2one(
        'account.journal',
        'Cuenta Bancaria',
        required=True,
        tracking=True
    )
    amount = fields.Monetary(
        'Importe total',
        compute='_get_checks_total',
        tracking=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        'Moneda',
        tracking=True
    )
    check_ids = fields.Many2many(
        'account.third.check',
        'third_check_deposit_slip_rel',
        'deposit_slip_id',
        'third_check_id',
        string='Cheques'
    )
    state = fields.Selection(
        [('canceled', 'Cancelada'),
         ('draft', 'Borrador'),
         ('deposited', 'Depositada')],
        string='Estado',
        default='draft',
        tracking=True
    )
    move_ids = fields.One2many(
        'account.move',
        'deposit_slip_id',
        'Asientos contables',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Compania',
        required=True,
        default=lambda self: self.env.company,
    )

    _sql_constraints = [('name_uniq', 'unique(name, company_id)', 'Ya existe una boleta de depósito con ese nombre.')]

    _order = "date desc, name desc"

    @api.constrains('check_ids', 'journal_id')
    def check_currency(self):
        """ Valida que no haya cheques con distintas monedas """
        for r in self:
            journal_currency = r.journal_id.currency_id or r.journal_id.company_id.currency_id
            if r.check_ids and journal_currency != r.check_ids.mapped('currency_id'):
                exceptions.different_currency_deposit()

            r.check_ids.deposit_slip_constraints()

    def post(self):
        """ Confirma la boleta de deposito cambiando el estado de los cheques y crea el asiento correspondiente """
        for deposit_slip in self:
            if not deposit_slip.check_ids:
                exceptions.no_checks_in_deposit()
            if any(check.state != 'wallet' for check in self.check_ids):
                exceptions.no_checks_in_wallet()

            deposit_slip.write({
                # Ya validamos en el constraint que la moneda es unica
                'currency_id': deposit_slip.check_ids.mapped('currency_id').id,
                'state': 'deposited'
            })
            for check in deposit_slip.check_ids:
                deposit_slip.move_ids |= deposit_slip._create_move(check)
            deposit_slip.check_ids.post_deposit_slip()

    def cancel_to_draft(self):
        """ Vuelve una boleta a estado borrador """
        self.ensure_one()
        self.state = 'draft'

    def cancel_deposit_slip(self):
        """ Cancela la boleta de deposito y elimina el asiento """
        self.ensure_one()
        # Cancelamos y borramos el asiento
        self.move_ids.button_draft()
        self.move_ids.button_cancel()
        self.move_ids.with_context(force_delete=True).unlink()

        # Revertimos el estado de los cheques
        self.check_ids.cancel_deposit_slip()

        self.state = 'canceled'

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            values['name'] = self.env['ir.sequence'].next_by_code('account.deposit.slip.sequence')
        return super(AccountDepositSlip, self).create(vals_list)
    
    def _create_check_move(self, check):
        vals = {
            'name': '/',
            'date': self.date,
            'ref': 'Boleta de depósito {}{}: {}'.format(
                self.name, " ({})".format(self.reference) if self.reference else '', check.name),
        }
        move = self.env['account.move'].with_context(default_journal_id=check.journal_id.id).create(vals)
        # Hacemos el cómputo multimoneda
        company = self.env.company
        company_currency = company.currency_id
        # Creamos las líneas de los asientos
        # Se calcula el debe del apunte con cuenta a debitar sumando los importes parciales que se van obteniendo de la
        # conversión de los montos de los cheques, así se evitan errores de redondeo
        company_currency_amount = self.currency_id._convert(check.amount, company_currency, company, self.date)
        amount_currency = check.amount
        self._create_move_line(move, self.company_id.transfer_account_id, check, amount_currency, debit=company_currency_amount)
        self._create_move_line(move, check.journal_id._get_journal_inbound_outstanding_payment_accounts()[0], check, -amount_currency, credit=company_currency_amount)
        return move
    
    def _create_deposit_move(self, check):
        vals = {
            'name': '/',
            'date': self.date,
            'ref': 'Boleta de depósito {}{}: {}'.format(
                self.name, " ({})".format(self.reference) if self.reference else '', check.name),
        }
        move = self.env['account.move'].with_context(default_journal_id=self.journal_id.id).create(vals)
        # Hacemos el cómputo multimoneda
        company = self.env.company
        company_currency = company.currency_id
        # Creamos las líneas de los asientos
        # Se calcula el debe del apunte con cuenta a debitar sumando los importes parciales que se van obteniendo de la
        # conversión de los montos de los cheques, así se evitan errores de redondeo
        company_currency_amount = self.currency_id._convert(check.amount, company_currency, company, self.date)
        amount_currency = check.amount
        self._create_move_line(move, self.journal_id._get_journal_inbound_outstanding_payment_accounts()[0], check, amount_currency, debit=company_currency_amount)
        self._create_move_line(move, self.company_id.transfer_account_id, check, -amount_currency, credit=company_currency_amount)
        return move

    def _create_move(self, check):
        """
        Crea el asiento de la boleta de depósito
        :param check: Cheque sobre el cual se creará el move
        :return: account.move creado
        """

        moves = self.env['account.move']
        
        move = self._create_check_move(check)
        move.action_post()
        moves |= move

        move = self._create_deposit_move(check)
        move.action_post()
        moves |= move

        # Concilio las cuentas puente del asiento del cheque y del asiento de la boleta de depósito
        moves.line_ids.filtered(
            lambda l: l.account_id == self.company_id.transfer_account_id and not l.reconciled
        ).reconcile()
        
        return moves

    def get_move_line_vals(self, move, account, company_currency, amount_currency, debit, credit, check):
        """Método auxiliar para estructurar en un dict los datos
        de los apuntes y hacer más extensible para herencia"""
        return {
            'partner_id': check.partner_id.id,
            'move_id': move.id,
            'debit': debit,
            'credit': credit,
            'amount_currency': amount_currency,
            'name': check.get_move_line_label_with_number(),
            'account_id': account.id,
            'journal_id': self.journal_id.id,
            'currency_id': check.currency_id != company_currency and check.currency_id.id
            or check.company_id.currency_id.id,
            'ref': move.ref
        }

    def _create_move_line(self, move, account, check, amount_currency, debit=0.0, credit=0.0):
        """
        Crea una move line de la boleta de deposito y las asocia al move
        :param move: account.move - Asiento a relacionar las move_lines creadas
        :param debit: Importe en el haber de la move line
        :param credit: Importe en el haber de la move line
        :return: account.move.line creada
        """

        company_currency = self.env.company.currency_id

        if not account:
            raise ValidationError("Falta configurar la cuenta de depósito en la cuenta bancaria"
                                  " o las cuentas en el diario del cheque.")

        move_line_vals = self.get_move_line_vals(move, account, company_currency, amount_currency, debit, credit, check)
        return self.env['account.move.line'].with_context(check_move_validity=False).create(move_line_vals)

    def view_moves(self):
        self.ensure_one()
        res = {
            'type': 'ir.actions.act_window',
            'views': [[False, 'form']],
            'res_model': 'account.move',
        }
        domain = [('deposit_slip_id', '=', self.id)]
        moves = self.env['account.move'].search(domain)
        if len(moves) == 1:
            res['res_id'] = moves[0].id
        else:
            res['name'] = "Asientos de {}".format(self.name)
            res['views'].insert(0, [False, 'list'])
            res['domain'] = domain
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
