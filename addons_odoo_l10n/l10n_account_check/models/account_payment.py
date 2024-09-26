# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from ..exceptions import exceptions


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

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if res.get("company_id") == False:
            res["company_id"] = self.env.company.id
        return res


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

    @api.depends('date')
    def compute_check_issue_date(self):
        for payment in self:
            payment.check_issue_date = payment.date or fields.Date.today()

    @api.onchange('account_third_check_sent_ids')
    def onchange_third_checks_sent(self):
        for r in self.account_third_check_sent_ids.filtered(lambda c: not c.sent_rate):
            orig_check = r._origin
            rate = self.env['res.currency']._get_conversion_rate(
                self.currency_id, orig_check.currency_id, self.company_id, self.date)
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
            if payment.payment_type == 'outbound' and payment.account_third_check_ids:
                exceptions.wrong_checks_outbound_payment()
            elif payment.payment_type == 'inbound' and\
                    (payment.account_own_check_ids or payment.account_third_check_sent_ids):
                exceptions.wrong_checks_inbound_payment()

    def action_post(self):
        """ Heredamos la función para cambiar los estados de los cheques """
        for payment in self:
            payment.account_third_check_ids.post_receipt()
            payment.account_third_check_sent_ids.post_payment()
            payment.account_own_check_ids.post_payment({'destination_payment_id': payment.id})

        return super(AccountPayment, self).action_post()

    def action_draft(self):
        """ Heredamos la función para cambiar los estados de los cheques """
        for payment in self:
            if payment.state != 'cancel':
                payment.account_third_check_ids.cancel_receipt()
                payment.account_third_check_sent_ids.cancel_payment()
                payment.account_own_check_ids.cancel_payment()

        return super(AccountPayment, self).action_draft()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'company_id' not in vals:
                vals['company_id'] = self.env.company.id
            if self.env.context.get('default_is_internal_transfer', False) and 'is_internal_transfer' not in vals:
                vals['is_internal_transfer'] = True
            if self.env.context.get('default_payment_type', False) and 'payment_type' not in vals:
                vals['payment_type'] = self.env.context.get('default_payment_type')
        return super().create(vals_list)

    def write(self, vals):
        if self.env.context.get('default_is_internal_transfer', False) and not self.is_internal_transfer and self.payment_type == self.env.context.get('default_payment_type'):
            vals['is_internal_transfer'] = True
        return super().write(vals)

    def action_paired_internal_transfer_payment_id(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Transferencias internas',
            'res_model': 'account.payment',
            'view_mode': 'form',
            'res_id': self.paired_internal_transfer_payment_id.id,
            'context': dict(self._context, create=False, default_company_id=self.company_id.id)
        }
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
