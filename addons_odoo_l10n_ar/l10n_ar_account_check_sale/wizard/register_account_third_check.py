# -*- encoding: utf-8 -*-

from odoo import models, fields


class RegisterAccountThirdCheck(models.TransientModel):
    _inherit = 'register.account.third.check'

    # Redefino la tabla de m2m ya que account.third.check ya tiene un sold_check_ids con tabla y columnas declarados,
    # y Odoo no deja que dos modelos distintos (tengan herencia entre sí o no) tengan dos m2m iguales (lo que sucedería
    # si no redefino la tabla y columnas acá y reutilizo las del campo heredado).
    sold_check_ids = fields.Many2many(
        'account.sold.check',
        'register_third_check_sold_check_rel',
        'register_third_check_id',
        'sold_check_id',
        string='Documentos de venta de cheques'
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
