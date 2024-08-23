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

    voucher_name = fields.Char(
        'Numero documento',
        copy=False
    )
    voucher_type_id = fields.Many2one(
        'voucher.type',
        compute='_compute_voucher_type_id',
        readonly=False,
        store=True,
        ondelete='restrict',
        copy=True
    )

    @api.depends('payment_type')
    def _compute_voucher_type_id(self):
        for payment in self:
            voucher_type = self.env['voucher.type'].search([
                ('category', '=', payment.payment_type == 'outbound' and 'payment_out'
                 or payment.payment_type == 'inbound' and 'payment_in'),
            ], limit=1)
            payment.voucher_type_id = voucher_type if voucher_type else None

    def post(self):
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
                'move_name': payment_name
            })
        return super(AccountPayment, self).post()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
