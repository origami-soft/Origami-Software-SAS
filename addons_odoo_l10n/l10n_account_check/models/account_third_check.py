# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from ..exceptions import exceptions


class AccountThirdCheck(models.Model):
    _inherit = 'account.abstract.check'
    _name = 'account.third.check'
    _description = 'Cheque de terceros'

    issue_name = fields.Char(
        'Emisor',
        tracking=True
    )
    destination_payment_id = fields.Many2one(
        'account.payment',
        'Pago destino',
        help="Pago donde se utilizó el cheque",
    )
    payment_register_ids = fields.Many2many('account.payment.register')
    not_to_order = fields.Boolean(
        string="No a la orden",
        help="Si está establecido, este cheque no podrá ser utilizado para realizar pagos."
    )
    sent_rate = fields.Float(
        string="Cotización de entrega",
        digits=(12, 6)
    )
    sent_payment_currency_amount = fields.Monetary(
        string="Monto en moneda de pago en entrega",
        currency_field='sent_payment_currency_id'
    )
    sent_payment_currency_id = fields.Many2one(
        related='destination_payment_id.currency_id',
        store=True
    )
    same_currency_as_sent_payment = fields.Boolean(
        compute='get_same_currency_as_sent_payment'
    )
    partner_id = fields.Many2one(
        related='payment_id.partner_id',
        string="Partner de Origen",
        store=True
    )
    destination_partner_id = fields.Many2one(
        related='destination_payment_id.partner_id',
        string="Partner de Destino",
        store=True
    )
    journal_id = fields.Many2one(
        domain="[('company_id', '=', company_id), ('payment_usage', '=', 'third_check')]"
    )

    @api.depends('currency_id', 'sent_payment_currency_id')
    def get_same_currency_as_sent_payment(self):
        for r in self:
            if r.env.context.get('payment_currency'):
                r.same_currency_as_sent_payment = r.currency_id.id == r.env.context.get('payment_currency')
            else:
                r.same_currency_as_sent_payment = r.currency_id == r.sent_payment_currency_id

    def validate_sent_rate(self):
        return all(not r.destination_payment_id or r.sent_rate > 0 for r in self)

    @api.constrains('sent_rate')
    def check_sent_rate(self):
        if not self.validate_sent_rate():
            exceptions.invalid_sent_rate()

    @api.onchange('sent_rate')
    def onchange_sent_rate(self):
        """ Al modificar el monto actualizo el monto en moneda de pago según la tasa de la línea """
        if self.env.context.get('sent_payment_currency_amount_modified'):
            return
        ctx = self.env.context.copy()
        ctx['sent_rate_modified'] = True
        self.env.context = ctx
        self.sent_payment_currency_amount = round(self.amount / self.sent_rate, 2) if self.sent_rate else 0

    @api.onchange('sent_payment_currency_amount')
    def onchange_sent_payment_currency_amount(self):
        """
        Al modificar el monto en moneda de pago actualizo la tasa (siempre y cuando la moneda del método y la del pago
        sean distintas, si son iguales actualizo el monto de la línea)
        """
        if self.env.context.get('sent_rate_modified'):
            return
        ctx = self.env.context.copy()
        ctx['sent_payment_currency_amount_modified'] = True
        self.env.context = ctx
        payment_amount = self.sent_payment_currency_amount
        if self.currency_id != self.sent_payment_currency_id:
            self.sent_rate = self.amount / payment_amount if payment_amount else 0

    def get_states(self):
        res = super(AccountThirdCheck, self).get_states()
        res.insert(2, ('deposited', 'Depositado'))
        res.insert(1, ('wallet', 'En cartera'))
        return res

    def _check_unlink_state(self):
        return self.state == 'draft'

    def unlink(self):
        if any(not r._check_unlink_state() for r in self):
            exceptions.delete_non_draft_check()
        super(AccountThirdCheck, self).unlink()

    def _check_post_receipt_state(self):
        return self.state == 'draft'

    def post_receipt(self):
        """ Lo que deberia pasar con el cheque cuando se valida un recibo """
        if any(not r._check_post_receipt_state() for r in self):
            exceptions.post_payment_non_draft_check()
        self.next_state('draft')

    def _check_post_payment_state(self):
        return self.state == 'wallet'

    def post_payment(self):
        """ Lo que deberia pasar con el cheque cuando se valida un pago """
        for r in self:
            if not r._check_post_payment_state():
                exceptions.post_payment_non_wallet_check()
            if r.not_to_order:
                exceptions.post_payment_not_to_order_check()
        self.next_state('wallet_handed')

    def _check_cancel_receipt_state(self):
        return self.state == 'wallet'

    def cancel_receipt(self):
        """ Lo que deberia pasar con el cheque cuando se cancela un recibo """
        if any(not check._check_cancel_receipt_state() for check in self):
            exceptions.cancel_receipt_non_wallet_check()
        self.cancel_state('wallet')

    def cancel_payment(self):
        """ Lo que deberia pasar con el cheque cuando se cancela una orden de pago """
        if any(not check._check_state_for_cancel_payment() for check in self):
            exceptions.cancel_payment_non_handed_check()
        self.cancel_state('handed')

    def get_cancel_states(self):
        return {
            'wallet': 'draft',
            'handed': 'wallet',
        }

    def get_next_states(self):
        return {
            'draft': 'wallet',
            'wallet_handed': 'handed',
        }

    def get_payment_currency_field(self, payment):
        return 'sent_payment_currency_id' if payment.payment_type == 'outbound' \
            else super(AccountThirdCheck, self).get_payment_currency_field(payment)

    def get_rate_field(self, payment):
        return 'sent_rate' if payment.payment_type == 'outbound' else super(AccountThirdCheck, self).get_rate_field(payment)

    def get_amount_field(self, payment):
        return 'sent_payment_currency_amount' if payment.payment_type == 'outbound' \
            else super(AccountThirdCheck, self).get_amount_field(payment)

    def get_name_for_move_line(self):
        return 'CHEQUE DE TERCEROS N° {}'.format(self.name)

    def get_move_vals(self, payment):
        # Se hereda este metodo, que proviene de account.abstract.payment.line, para poder modificar el partner que va a tener
        # el apunte contable (correspondiente al haber) del asiento correspondiente a este tipo de metodo de pago.
        # Con esto se cubre el caso de pagar un pago a proveedor con un cheque de terceros.
        res = super(AccountThirdCheck, self).get_move_vals(payment)
        for rec in res.get('line_ids',[]):
            if len(rec) > 2 and rec[2].get('credit', False):
                rec[2].update({'partner_id': self.partner_id.id if self.partner_id else res.get('partner_id',False)})
        return res

    def open_correct_wizard(self):
        res = super().open_correct_wizard()
        res['context'] = {'default_third_check_id': self.id}
        return res
    
    def rename_moves(self, previous_number):
        res = super().rename_moves(previous_number)
        new_move_line_name = self.get_first_move_line_name()
        move_line_name_array = new_move_line_name.split(' ')
        move_line_name_array[-1] = previous_number
        prev_move_line_name = ' '.join(move_line_name_array)
        move_lines = self.destination_payment_id.move_ids.line_ids.filtered(lambda l: l.name == prev_move_line_name)
        move_lines.write({'name': new_move_line_name})
        return res

    def modify_maturity_date(self, payment):
        # en el caso de pagos a proveedor con cheque de terceros, no se usa fecha de pago del cheque
        if payment.partner_type == 'supplier':
            return False
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
