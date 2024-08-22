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
from ..exceptions.exceptions import WrongChecksInOutboundPaymentError, WrongChecksInInboundPaymentError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # Cheques recibidos
    account_third_check_ids = fields.One2many(
        'account.third.check',
        'payment_id',
        'Cheques de terceros recibidos',
        copy=False
    )
    # Cheques entregados
    account_third_check_sent_ids = fields.One2many(
        'account.third.check',
        'destination_payment_id',
        'Cheques de terceros entregados',
        copy=False
    )
    account_own_check_ids = fields.One2many(
        'account.own.check',
        'payment_id',
        'Cheques propios',
        copy=False
    )
    check_issue_date = fields.Date(compute='compute_check_issue_date')

    def unlink(self):
        """ Heredo el método unlink() ya que al eliminar un pago,
        si no se define explícitamente eliminar las líneas también
        Odoo intentará poner NULL en todos los campos de las líneas,
        generando errores por constraint not null """
        for payment in self:
            payment.account_own_check_ids.unlink()
            if payment.payment_type == 'inbound':
                payment.account_third_check_ids.unlink()
            elif payment.payment_type == 'outbound':
                payment.account_third_check_sent_ids = None
        return super(AccountPayment, self).unlink()

    @api.onchange('account_third_check_ids', 'account_own_check_ids')
    def onchange_check_ids(self):
        self.recalculate_payment_amount()

    @api.depends('payment_date')
    def compute_check_issue_date(self):
        for payment in self:
            payment.check_issue_date = payment.payment_date or fields.Date.today()

    @api.onchange('account_third_check_sent_ids')
    def onchange_third_checks_sent(self):
        for r in self.account_third_check_sent_ids.filtered(lambda c: not c.sent_rate):
            orig_check = r._origin
            rate = self.env['res.currency']._get_conversion_rate(
                self.currency_id, orig_check.currency_id, self.company_id, self.payment_date)
            r.sent_rate = rate
            r.onchange_sent_rate()
        self.recalculate_payment_amount()

    def get_payment_line_fields(self):
        res = super(AccountPayment, self).get_payment_line_fields()
        res.extend(['account_third_check_ids', 'account_own_check_ids', 'account_third_check_sent_ids'])
        return res

    @api.constrains('account_third_check_ids', 'account_own_check_ids', 'account_third_check_sent_ids', 'payment_type')
    def constraint_checks(self):
        """ Nos aseguramos que tenga los cheques correspondientes cada tipo de pago y su estado """
        for payment in self:
            if payment.payment_type in ['outbound', 'transfer'] and payment.account_third_check_ids:
                raise WrongChecksInOutboundPaymentError("No puede haber cheques de terceros en este tipo de pago")

            elif payment.payment_type in ['inbound', 'transfer'] and\
                    (payment.account_own_check_ids or payment.account_third_check_sent_ids):
                raise WrongChecksInInboundPaymentError("No puede haber cheques propios o endosados en este tipo de pago")

    def post(self):
        """ Heredamos la función para cambiar los estados de los cheques """

        for payment in self:
            payment.account_third_check_ids.post_receipt()
            payment.account_third_check_sent_ids.post_payment()
            payment.account_own_check_ids.post_payment({'destination_payment_id': payment.id})

        return super(AccountPayment, self).post()

    def action_draft(self):
        """ Heredamos la función para cambiar los estados de los cheques """
        for payment in self:
            if payment.state != 'cancelled':
                payment.account_third_check_ids.cancel_receipt()
                payment.account_third_check_sent_ids.cancel_payment()
                payment.account_own_check_ids.cancel_payment()

        return super(AccountPayment, self).action_draft()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
