# -*- encoding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import ValidationError


class ChangeDatePaymentTypeWizard(models.TransientModel):
    _name = 'change.date.payment.type.wizard'
    _description = 'Cambiar Fecha'

    new_date = fields.Date("Nueva Fecha", required=True)

    def change_date(self):
        if self.new_date:
            # se cambia la fecha en los asientos
            active_model = self.env.context['active_model']
            active_id = self.env.context['active_id']
            line = self.env[active_model].browse(active_id)
            # busco los account.move relacionados al pago
            moves = self.env['account.move'].search([['account_abstract_line_id', '=', line.id]])
            # usado para asientos creados antes de la actualizacion
            if not moves:
                raise ValidationError("No es posible cambiar la fecha en este pago.")
            else:
                # cambio la fecha en la linea(account.payment.type.line)
                line.date = self.new_date
                # cambio fecha en los asientos contables del pago(account.move)
                for move in moves:
                    move.date = self.new_date
                    # cambio fecha en los apuntes contables
                    move.line_ids.with_context(skip_validation = True).write({'date': self.new_date})