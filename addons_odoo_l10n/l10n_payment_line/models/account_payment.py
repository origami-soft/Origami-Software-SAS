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
from ..exceptions.exceptions import NotEqualAmountsError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    show_payment_lines = fields.Boolean(compute='get_show_payment_lines')
    multiple_payment_journal = fields.Boolean(related='journal_id.multiple_payment_journal')
    line_move_ids = fields.One2many('account.move.line', 'payment_id')

    def unlink(self):
        """ Heredo el método unlink() ya que al eliminar un pago, 
        si no se define explícitamente eliminar las líneas también 
        Odoo intentará poner NULL en todos los campos de las líneas,
        generando errores por constraint not null """
        payment_line_fields = self.get_payment_line_fields()
        for payment in self:
            for payment_line in payment_line_fields:
                getattr(payment, payment_line).unlink()
        return super(AccountPayment, self).unlink()

    @api.onchange('journal_id')
    def _onchange_journal(self):
        if self.journal_id and not self.journal_id.currency_id:
            self.currency_id = self.journal_id.company_id.currency_id
        return super(AccountPayment, self)._onchange_journal()

    def get_payment_line_fields(self):
        return []

    def _get_show_payment_lines(self):
        return self.multiple_payment_journal and self.payment_type != 'transfer'

    @api.depends('payment_type', 'multiple_payment_journal')
    def get_show_payment_lines(self):
        for r in self:
            r.show_payment_lines = r._get_show_payment_lines()
    
    def recalculate_payment_amount(self):
        self.amount = self.get_payment_line_total()
    
    def get_journal_debit_account(self):
        return self.journal_id.default_debit_account_id.id

    def get_journal_credit_account(self):
        return self.journal_id.default_credit_account_id.id
    
    def get_second_payment_line_move_line_name(self):
        return self.name

    def get_payment_line_total(self):
        total = 0
        for recordset in self._get_payment_line_recordsets():
            total += sum(getattr(r, r.get_amount_field(self)) for r in recordset)
        return round(total, 2)

    def validate_equal_amounts(self):
        return all(not r.multiple_payment_journal or r.get_payment_line_total() == r.amount for r in self)

    @api.onchange('journal_id', 'currency_id', 'payment_date', 'company_id')
    def onchange_update_rates(self):
        """ Si cambio la compañía del pago o la fecha, actualizo las cotizaciones de las líneas """
        for recordset in self._get_payment_line_recordsets():
            for r in recordset:
                r.onchange_update_rate()
                r.onchange_amount()

    def _get_payment_line_recordsets(self):
        return [getattr(self, field) for field in self.get_payment_line_fields()]

    def _prepare_payment_moves(self):
        """
        Heredo la función que define los datos con los cuales se generarán los asientos para crear asientos adicionales
        en caso de que se definan métodos de pago (uno por cada método)
        """
        res = super(AccountPayment, self)._prepare_payment_moves()
        if self.payment_type != 'transfer':
            for recordset in self._get_payment_line_recordsets():
                for r in recordset:
                    res.append(r.get_move_vals(self))
        return res

    def post(self):
        """
        Paso por contexto que no se actualicen las cotizaciones de las líneas de métodos para evitar que la validación
        del pago pise las cotizaciones introducidas
        """
        if any(r.payment_type != 'transfer' and not r.validate_equal_amounts() for r in self):
            raise NotEqualAmountsError("El total de las grillas de pago debe coincidir con el total del pago.")
        res = super(AccountPayment, self.with_context(do_not_update_rates=True)).post()
        for r in self.filtered(lambda l: l.payment_type != 'transfer' and l.multiple_payment_journal):
            # Concilio entre sí todos los apuntes que tengan la cuenta del diario del pago (serán el apunte del pago y
            # los de las grillas)
            account = r.journal_id.default_credit_account_id if r.payment_type not in ('outbound', 'transfer') \
                else r.journal_id.default_debit_account_id
            r.move_line_ids.filtered(lambda l: l.account_id == account).reconcile()
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
