# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

MOVE_LINE_LABEL = "Registro de débito de cheque propio {}"


class WizardOwnCheckReconcile(models.TransientModel):
    _name = 'wizard.own.check.reconcile'
    _description = 'Wizard de registro de débito de cheque propio'

    def _get_lines(self):
        checks = self.env['account.own.check'].browse(self.env.context.get('active_ids'))
        self.validate_lines(checks)
        return [(0, 0, check.get_reconcile_vals()) for check in checks]

    def validate_lines(self, checks):
        valid_states = checks.get_reconcile_valid_check_states()
        if any(c.state not in valid_states for c in checks):
            raise ValidationError(checks.get_reconcile_check_state_error())
        if len(checks.mapped('company_id')) > 1:
            raise ValidationError("Los cheques seleccionados deben ser de la misma compañía.")

    date = fields.Date(
        default=fields.Date.context_today,
        string="Fecha",
        required=True,
    )

    line_ids = fields.One2many(
        comodel_name='wizard.own.check.reconcile.line',
        inverse_name='reconcile_id',
        string="Líneas",
        default=_get_lines,
    )

    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self._get_default_company(),
    )

    def _get_default_company(self):
        checks = self.env['account.own.check'].browse(self.env.context.get('active_ids'))
        return checks.mapped('company_id')[0] if checks and checks.mapped('company_id') else self.env.company

    @api.model
    def create(self, vals):
        """
        Redefino el create porque al confirmar en el popup se crea el objeto y pierdo la referencia a las líneas
        :param vals: valores de la creacion
        :return: objeto creado
        """
        res = super(WizardOwnCheckReconcile, self).create(vals)
        if vals.get('line_ids') and not res.line_ids:
            line_ids = [val[1] for val in vals['line_ids']]
            res.line_ids = [(6, 0, line_ids)]
        return res

    def get_move_line_vals(self, move, account, amount_currency, line_currency, check, debit=0.0, credit=0.0):
        return {
            'partner_id': check.destination_partner_id.id if check.destination_partner_id else False,
            'name': MOVE_LINE_LABEL.format(check.name),
            'account_id': account.id,
            'date': self.date,
            'credit': credit,
            'debit': debit,
            'move_id': move.id,
            'amount_currency': amount_currency,
            'currency_id': line_currency,
        }

    def confirm(self):
        self.ensure_one()
        if not self.line_ids:
            raise ValidationError("El registro de débito a confirmar no posee líneas.")
        if any(not l.check_account_id for l in self.line_ids):
            raise ValidationError("La cuenta bancaria no tiene cuentas contables configuradas.\n"
                                  "Por favor, configurarlas en el diario correspondiente.")

        move_line_proxy = self.env['account.move.line'].with_context(check_move_validity=False)
        moves = self.env['account.move']

        for line in self.line_ids:
            check_moves = self.env['account.move']
            check = line.check_id
            company = self.env.company
            company_currency = company.currency_id
            line_currency = check.currency_id.id
            company_currency_amount = check.currency_id._convert(line.amount, company_currency, company, self.date)
            amount_currency = line.amount

            move = self.env['account.move'].with_context(default_journal_id=check.journal_id.id).create({
                'date': self.date,
                'ref': 'Registro de débito de cheques propios {}'.format(self.date.strftime('%d/%m/%Y')),
            })
            move_line_proxy.create(self.get_move_line_vals(
                move, line.check_account_id, amount_currency, line_currency, check, debit=company_currency_amount
            ))
            move_line_proxy.create(self.get_move_line_vals(
                move, company.transfer_account_id, -amount_currency, line_currency, check, credit=company_currency_amount
            ))
            move.action_post()
            check_moves |= move

            move = self.env['account.move'].with_context(default_journal_id=check.bank_journal_id.id).create({
                'date': self.date,
                'ref': 'Registro de débito de cheques propios {}'.format(self.date.strftime('%d/%m/%Y')),
            })
            move_line_proxy.create(self.get_move_line_vals(
                move, company.transfer_account_id, amount_currency, line_currency, check, debit=company_currency_amount
            ))
            move_line_proxy.create(self.get_move_line_vals(
                move, line.account_id, -amount_currency, line_currency, check, credit=company_currency_amount
            ))
            move.action_post()
            check_moves |= move

            check.reconcile_check({'reconcile_move_ids': check_moves, 'reconcile_date': self.date})
            moves |= check_moves

        # Concilio las cuentas puente del asiento del cheque y del asiento del débito
        moves.line_ids.filtered(lambda l: l.account_id == company.transfer_account_id).reconcile()
        
        res = {
            'type': 'ir.actions.act_window',
            'views': [[False, 'form']],
            'res_model': 'account.move',
        }
        if len(moves) == 1:
            res['res_id'] = moves[0].id
        else:
            res['name'] = "Asientos de débito"
            res['views'].insert(0, [False, 'list'])
            res['domain'] = [('id', 'in', moves.ids)]
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
