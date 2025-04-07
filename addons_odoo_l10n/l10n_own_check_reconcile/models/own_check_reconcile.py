# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class OwnCheckReconcile(models.Model):
    _name = 'own.check.reconcile'
    _description = 'Conciliación de cheque propio'
    _inherit = 'mail.thread'

    def _get_lines(self):
        checks = self.env['account.own.check'].browse(self.env.context.get('active_ids'))
        self.validate_lines(checks)
        return [(0, 0, {'check_id': check.id,
                        'amount': check.amount,
                        'check_account_id': check.journal_id.default_debit_account_id.id,
                        'currency_id': check.currency_id.id}) for check in checks]

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

    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string="Diario",
        check_company=True
    )

    general_account_id = fields.Many2one(
        comodel_name='account.account',
        string="Cuenta general",
        check_company=True
    )

    move_id = fields.Many2one(
        comodel_name='account.move',
        string="Asiento",
        readonly=True,
    )

    line_ids = fields.One2many(
        comodel_name='own.check.reconcile.line',
        inverse_name='reconcile_id',
        string="Líneas",
        default=_get_lines,
    )

    state = fields.Selection(
        string="Estado",
        selection=[
            ('draft', 'Borrador'),
            ('confirmed', 'Confirmada'),
            ('canceled', 'Cancelada'),
        ],
        required=True,
        default='draft',
        tracking=True,
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

    @api.depends('date', 'journal_id.name')
    def _compute_display_name(self):
        for r in self:
            r.display_name = "{} - {}".format(r.date.strftime('%d/%m/%Y'), r.journal_id.name)

    @api.model
    def create(self, vals):
        """
        Redefino el create porque al confirmar en el popup se crea el objeto y pierdo la referencia a las lineas
        :param vals: valores de la creacion
        :return: objeto creado
        """
        res = super(OwnCheckReconcile, self).create(vals)
        if vals.get('line_ids') and not res.line_ids:
            line_ids = [val[1] for val in vals['line_ids']]
            res.line_ids = [(6, 0, line_ids)]
        return res

    def unlink(self):
        if 'confirmed' in self.mapped('state'):
            raise ValidationError("No se pueden eliminar conciliaciones confirmadas.")
        return super(OwnCheckReconcile, self).unlink()

    def cancel(self):
        for r in self:
            r.move_id.button_cancel()
            r.move_id.with_context(force_delete=True).unlink()
            r.line_ids.mapped('check_id').cancel_reconcile()
        self.write({
            'state': 'canceled',
        })

    @api.onchange('company_id')
    def onchange_company(self):
        if not self.env.context.get('not_company_change'):
            self.update({'line_ids': [(6, 0, [])], 'journal_id': False})

    @api.onchange('journal_id')
    def onchange_journal(self):
        self.general_account_id = self.journal_id.default_credit_account_id.id

    @api.onchange('general_account_id')
    def onchange_general_account(self):
        self.line_ids.update({'account_id': self.general_account_id})

    def get_move_line_vals(self, move, account, amount_currency, line_currency, check, debit=0.0, credit=0.0):
        """Método auxiliar para estructurar en un dict los datos 
        de los apuntes y hacer más extensible para herencia"""
        return {
            'partner_id': check.destination_partner_id.id if check.destination_partner_id and debit else False,
            'name': 'Conciliación de cheque propio {}'.format(check.name),
            'account_id': account.id,
            'journal_id': self.journal_id.id,
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
            raise ValidationError("La conciliación a confirmar no posee lineas.")
        if any(not l.check_account_id for l in self.line_ids):
            raise ValidationError("La cuenta bancaria no tiene cuentas contables configuradas.\n"
                                  "Por favor, configurarlas en el diario correspondiente.")

        move_line_proxy = self.env['account.move.line'].with_context(check_move_validity=False)

        date = self.date.strftime('%d/%m/%Y')
        move = self.env['account.move'].with_context(default_journal_id=self.journal_id.id).create({
            'state': 'draft',
            'date': self.date,
            'ref': 'Conciliación de cheques propios {}'.format(date)
        })

        for line in self.line_ids:
            check = line.check_id
            company = self.env.company
            company_currency = company.currency_id
            line_currency = check.currency_id.id if check.currency_id != company_currency else False
            company_currency_amount = check.currency_id._convert(line.amount, company_currency, company, self.date)
            amount_currency = line.amount if line_currency else 0

            move_line_vals = self.get_move_line_vals(move, line.check_account_id, amount_currency, line_currency, check, debit=company_currency_amount)
            move_line_proxy.create(move_line_vals)
            move_line_vals = self.get_move_line_vals(move, line.account_id, -amount_currency, line_currency, check, credit=company_currency_amount)
            move_line_proxy.create(move_line_vals)
            check.reconcile_check({'reconcile_id': self.id})

        move.post()
        self.write({
            'move_id': move.id,
            'state': 'confirmed',
        })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
