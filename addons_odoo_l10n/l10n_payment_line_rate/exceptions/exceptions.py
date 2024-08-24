# -*- encoding: utf-8 -*-

from odoo.exceptions import ValidationError


def invalid_natural_rate_error():
    raise ValidationError("La cotización de la línea debe ser mayor o igual a 1.")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
