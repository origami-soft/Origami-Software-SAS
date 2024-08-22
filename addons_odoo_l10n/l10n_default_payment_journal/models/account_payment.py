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


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def get_default_payment_journal(self):
        journal_id = self.env['res.company'].browse(
            self._context.get('force_company', self.env.company.id)
        ).default_payment_journal_id.id
        return journal_id

    journal_id = fields.Many2one(default=get_default_payment_journal)

    def action_register_payment(self):
        """ Al abrir la ventana para registrar pagos, hago que el diario por defecto sea el definido en la compañía """
        res = super(AccountPayment, self).action_register_payment()
        new_context = res['context'].copy()
        new_context.update({'default_journal_id': self.get_default_payment_journal()})
        res['context'] = new_context
        return res

    @api.onchange('amount', 'currency_id')
    def _onchange_amount(self):
        """
        Si el pago no tiene diario, la función original va a establecerle uno según el tipo y compañía correspondientes
        así que, si se da ese caso, limpio el diario nuevamente
        """
        curr_journal = self.journal_id
        res = super(AccountPayment, self)._onchange_amount()
        if not (curr_journal or self.env.company.default_payment_journal_id):
            self.journal_id = False
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
