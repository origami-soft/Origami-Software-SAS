# -*- encoding: utf-8 -*-

from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def write(self, vals):
        """ En caso de que se esté realizando un write solamente para anexar una línea de seguimiento o marcarlo para
        excluir o no, me salteo la sincronización entre asiento y pago para evitar disparar validaciones de apuntes a
        cobrar/pagar, en distinta moneda, etc., que pueden darse en pagos arrastrados de versiones anteriores
        """
        if not vals.keys() - {'followup_line_id', 'blocked'}:
            self = self.with_context(skip_account_move_synchronization=True)
        return super().write(vals)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
