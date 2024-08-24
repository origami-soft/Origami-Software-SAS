# -*- encoding: utf-8 -*-

from odoo.exceptions import ValidationError


def different_currency_deposit():
    raise ValidationError("La moneda de los cheques es distinta a la de la cuenta bancaria de la boleta.")

def no_checks_in_deposit():
    raise ValidationError("No se puede validar una boleta sin cheques.")

def no_checks_in_wallet():
    raise ValidationError("Existen cheques en la boleta que no se encuentran en estado 'En cartera'. Elimínelos para poder validar la boleta.")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
