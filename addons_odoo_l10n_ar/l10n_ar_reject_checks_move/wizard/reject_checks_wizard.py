# -*- encoding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import ValidationError


class RejectChecksWizard(models.TransientModel):

    _name = 'reject.checks.wizard'
    _description = 'Rechazo de Cheques Wizard'

    create_moves = fields.Boolean(string='Generar asientos')
    reject_date = fields.Date(string="Fecha de rechazo", default=fields.Date.context_today, required=True)
    check_state = fields.Selection([
        ('draft', 'Borrador'),
        ('sold', 'Vendido'),
        ('handed', 'Entregado'),
        ('wallet', 'En cartera'),
        ('collect', 'Cobrado'),
        ('deposited', 'Depositado')
    ], string='Estado')

    def reject_check_wizard(self):
        check_id = self.env.context.get('active_id')
        model = self.env.context.get('active_model')
        check = self.env[model].browse(check_id)
        if self.create_moves and check.reject_move_id:
            raise ValidationError("El cheque contiene el asiento {} generado en un rechazo anterior. "
                                  "Por favor elimínelo o revierta el rechazo e intente nuevamente.".format(check.reject_move_id.name))
        else:
            if self.create_moves and not check.reject_move_id:
                check.create_reject_move(self.reject_date)
            check.reject_check()
            check.reject_date = self.reject_date

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
