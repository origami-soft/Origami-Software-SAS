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
from odoo.exceptions import ValidationError

RETENTION_TYPE_CODES = {
    'profit': 'profit',
    'vat': 'vat',
    'gross_income': 'gross',
    'other': 'other',
}


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    retention_ids = fields.One2many(
        'account.payment.retention',
        'payment_id',
        'Retenciones'
    )

    @api.onchange('retention_ids')
    def onchange_retention_ids(self):
        self.recalculate_payment_amount()

    def post(self):
        for rec in self.filtered(lambda ap: ap.partner_type == 'supplier'):
            rec.retention_ids.filtered(lambda x: not x.date).write({'date': rec.payment_date})
            for ret in rec.retention_ids.filtered(lambda x: not x.certificate_no):
                ret.certificate_no = self.env['ir.sequence'].with_context(force_company=rec.company_id.id).next_by_code(
                    'rtl.{}.seq'.format(RETENTION_TYPE_CODES.get(ret.retention_id.type)))
                if not ret.certificate_no:
                    raise ValidationError("No se encontró secuencia para la retencion: {RETENCION}".format(
                        RETENCION=ret.retention_id.name))
        return super(AccountPayment, self).post()

    def get_payment_line_fields(self):
        res = super(AccountPayment, self).get_payment_line_fields()
        res.extend(['retention_ids'])
        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
