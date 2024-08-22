# -*- encoding: utf-8 -*-

from odoo import models, fields


class RegisterAccountThirdCheck(models.TransientModel):
    _inherit = 'register.account.third.check'

    # Redefino la tabla de m2m ya que account.third.check ya tiene un deposit_slip_ids con tabla y columnas declarados,
    # y Odoo no deja que dos modelos distintos (tengan herencia entre sí o no) tengan dos m2m iguales (lo que sucedería
    # si no redefino la tabla y columnas acá y reutilizo las del campo heredado).
    deposit_slip_ids = fields.Many2many(
        'account.deposit.slip',
        'register_third_check_deposit_slip_rel',
        'register_third_check_id',
        'deposit_slip_id',
        string='Boletas de deposito'
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
