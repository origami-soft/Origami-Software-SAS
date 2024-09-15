# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

RETENTION_TYPE_CODES = {
    'profit': 'profit',
    'vat': 'vat',
    'gross_income': 'gross',
}


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    retention_ids = fields.One2many(
        'account.payment.retention',
        'payment_id',
        'Retenciones'
    )

    def unlink(self):
        """ Heredo el método unlink() ya que al eliminar un pago,
        si no se define explícitamente eliminar las líneas también
        Odoo intentará poner NULL en todos los campos de las líneas,
        generando errores por constraint not null """
        for payment in self:
            payment.retention_ids.unlink()
        return super(AccountPayment, self).unlink()

    @api.onchange('retention_ids')
    def onchange_retention_ids(self):
        self.recalculate_payment_amount()

    def action_post(self):
        for rec in self.filtered(lambda ap: ap.partner_type == 'supplier'):
            rec.retention_ids.filtered(lambda x: not x.date).write({'date': rec.date})
            for ret in rec.retention_ids.filtered(lambda x: not x.certificate_no):
                ret.certificate_no = self.env['ir.sequence'].with_company(rec.company_id).next_by_code(
                    'rtl.{}.seq'.format(RETENTION_TYPE_CODES.get(ret.retention_id.type)))
                if not ret.certificate_no:
                    raise ValidationError("No se encontró secuencia para la retencion: {RETENCION}".format(
                        RETENCION=ret.retention_id.name))
        return super(AccountPayment, self).action_post()

    def get_payment_line_fields(self):
        res = super(AccountPayment, self).get_payment_line_fields()
        res.extend(['retention_ids'])
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
