# -*- encoding: utf-8 -*-

from odoo import models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def unlink(self):
        if any(move.posted_before and move._check_electronic_invoice_sent() for move in self):
            raise ValidationError("No es posible eliminar facturas que ya fueron validadas electrónicamente")
        return super().unlink()

    def _check_electronic_invoice_sent(self):
        pass

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
