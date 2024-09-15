# -*- encoding: utf-8 -*-

from odoo import models, fields


class AccountPayment(models.Model):

    _inherit = 'account.payment'

    voucher_name = fields.Char(
        'Numero documento',
        copy=False
    )

    can_edit_wizard = fields.Boolean(string="Can Edit Wizard", compute='_compute_can_edit_wizard')

    def _compute_can_edit_wizard(self):
        for record in self:
            record.can_edit_wizard = False

    def _get_batches(self):
        pass


    def action_post(self):
        for payment in self.filtered(lambda x: x.journal_id.pos_ar_id):
            if not payment.voucher_name:
                payment.voucher_name = '{}-{}'.format(
                    payment.journal_id.pos_ar_id.name.zfill(payment.journal_id.pos_ar_id.prefix_quantity or 0),
                    payment.journal_id.pos_ar_id.next_number(payment.voucher_type_id)
                )
            payment_name = '{}{}'.format(
                    payment.voucher_type_id.prefix + ' ' if payment.voucher_type_id.prefix else '',
                    payment.voucher_name
                )
            payment.write({
                'name': payment_name,
            })
        return super(AccountPayment, self).action_post()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
