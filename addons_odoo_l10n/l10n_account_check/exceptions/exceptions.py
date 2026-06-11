# -*- encoding: utf-8 -*-

from odoo.exceptions import ValidationError


def post_payment_non_draft_check():
    raise ValidationError("Los cheques propios a utilizar deben estar en borrador.")

def non_numeric_check():
    raise ValidationError("El número del cheque solamente puede contener números.")

def invalid_check_dates():
    raise ValidationError("La fecha de pago del cheque no puede ser anterior a la fecha de emisión.")

def non_equal_check_dates():
    raise ValidationError("Las fechas de pago y emisión de un cheque común deben ser iguales.")

def delete_non_draft_check():
    raise ValidationError("Solamente se pueden borrar cheques en borrador.")

def post_receipt_non_draft_check():
    raise ValidationError("Los cheques de terceros recibidos deben estar en borrador.")

def post_payment_non_wallet_check():
    raise ValidationError("Los cheques de terceros entregados deben estar en cartera.")

def post_payment_not_to_order_check():
    raise ValidationError('No se puede validar un pago con cheques que son "no a la orden".')

def cancel_receipt_non_wallet_check():
    raise ValidationError("Los cheques de terceros deberian estar en cartera o en borrador para poder cancelar el pago.")

def cancel_payment_non_handed_check():
    raise ValidationError("Los cheques deben estar entregados o en cartera para cancelar el pago.")

def invalid_check_cancel_state():
    raise ValidationError("No se puede cancelar el cheque en el estado actual.")

def invalid_check_next_state():
    raise ValidationError("No se puede avanzar el cheque en el estado actual.")

def wrong_checks_outbound_payment():
    raise ValidationError("No puede haber cheques de terceros en este tipo de pago")

def wrong_checks_inbound_payment():
    raise ValidationError("No puede haber cheques propios o endosados en este tipo de pago")

def invalid_sent_rate():
    raise ValidationError("La cotización de la línea debe ser positiva.")

def duplicate_third_check_warning(check_number, amount, bank_name, partner_name):
    raise ValidationError(
        f"El cheque número [{check_number}] con importe [{amount}], "
        f"emitido por el banco [{bank_name}] del cliente [{partner_name}] "
        f"ya fue registrado en el sistema previamente. Revise los datos ingresados"
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
