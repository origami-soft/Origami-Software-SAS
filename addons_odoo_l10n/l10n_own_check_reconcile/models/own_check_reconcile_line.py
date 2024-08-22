# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

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
