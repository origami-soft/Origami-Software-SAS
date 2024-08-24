# - coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    bank_reconciled = fields.Boolean(
        string='Conciliado',
        copy=False
    )

    def write(self, vals):
        for move_line in self:
            if (vals.get('debit') or vals.get('credit') or vals.get('account_id')) and move_line.bank_reconciled:
                raise ValidationError('No se puede modificar un movimiento que'
                                      ' ya ha sido conciliado bancariamente.')
        return super(AccountMoveLine, self).write(vals)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
