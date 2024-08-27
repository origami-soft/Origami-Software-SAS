# -*- encoding: utf-8 -*-

from odoo import models, fields


class RegisterAccountThirdCheck(models.TransientModel):
    _name = 'register.account.payment.retention'
    _inherit = ['account.payment.retention', 'register.account.abstract.payment.line']
    _description = 'Retenciones en "Registrar pago"'

    payment_date = fields.Date(
        string='Fecha',
        related='payment_id.payment_date',
        readonly=True
    )

    def get_payment_line_vals(self):
        res = super().get_payment_line_vals()
        res.update({
            'base': self.base,
            'aliquot': self.aliquot,
            'date': self.date,
            'retention_id': self.retention_id.id,
            'certificate_no': self.certificate_no,
            'type': self.type,
            'jurisdiction': self.jurisdiction,
            'activity_id': self.activity_id.id
        })
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
