# - coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountBankReconcile(models.Model):
    _name = 'account.bank.reconcile'
    _description = 'Conciliación bancaria'

    name = fields.Char(
        string='Nombre',
        required=True,
    )
    account_id = fields.Many2one(
        comodel_name='account.account',
        string='Cuenta',
        required=True,
        domain=[('account_type', '=', 'asset_cash')]
    )
    bank_reconcile_line_ids = fields.One2many(
        comodel_name='account.bank.reconcile.line',
        inverse_name='bank_reconcile_id',
        string='Conciliaciones',
        limit=12,
    )
    unreconciled_count = fields.Integer(
        'Elementos sin conciliar',
        compute='_get_unreconciled')
    company_id = fields.Many2one(
        'res.company',
        string='Compania',
        required=True,
        default=lambda self: self.env.company,
    )

    def open_unreconciled_move_lines(self):
        return {
            'name': 'Movimientos sin conciliar',
            'views': [[False, "tree"]],
            'domain': [('account_id', '=', self.account_id.id), ('bank_reconciled', '=', False), ('move_id.state', '=', 'posted')],
            'res_model': 'account.move.line',
            'type': 'ir.actions.act_window',
        }

    # Cantidad de movimientos sin conciliar
    def _get_unreconciled(self):
        for r in self:
            r.unreconciled_count = r.env['account.move.line'].search_count([
                ('bank_reconciled', '=', False),
                ('account_id', '=', r.account_id.id),
                ('move_id.state', '=', 'posted')
            ])

    # Chequeo si existen concialiaciones antes de eliminar una conciliacion bancaria
    def unlink(self):
        for bank in self:
            if bank.bank_reconcile_line_ids:
                raise ValidationError(
                    'No se puede eliminar una conciliacion bancaria con conciliaciones realizadas. Primero '
                    'elimine las conciliaciones relacionadas.'
                )
        return super(AccountBankReconcile, self).unlink()

    def write(self, vals):
        if vals.get('account_id') and len(self.bank_reconcile_line_ids) > 0:
            raise ValidationError('No se puede modificar la cuenta si ya tiene movimientos conciliados')
        return super(AccountBankReconcile, self).write(vals)

    def get_last_conciliation(self):
        return self.bank_reconcile_line_ids.sorted(key=lambda x: x.date_stop, reverse=True)[0] \
            if self.bank_reconcile_line_ids else False

    _sql_constraints = [(
        'account_unique',
        'unique(account_id)',
        'Ya existe una conciliacion con esta cuenta.'
    )]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
