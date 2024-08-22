# -*- encoding: utf-8 -*-

from odoo.exceptions import ValidationError


def invalid_amount(line_description):
    raise ValidationError("El monto de la línea de {} debe ser positivo.".format(line_description))

def invalid_rate(line_description):
    raise ValidationError("La cotización de la línea de {} debe ser positiva.".format(line_description))

def no_account(journal):
    raise ValidationError("El diario {} no posee cuenta predeterminada.".format(journal))

def not_equal_amounts():
    raise ValidationError("El total de las grillas de pago debe coincidir con el total del pago.")

def journal_and_payment_on_different_currency(journal, payment_currency):
    raise ValidationError("La moneda del diario {} es diferente de la del pago {}.".format(journal.name, payment_currency.name))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
