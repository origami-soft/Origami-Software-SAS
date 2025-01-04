# -*- coding: utf-8 -*-

from odoo import models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _post(self, soft=True):
        """Heredo método para actualizar la referencia de los asientos diferidos una vez
        fueron publicados
        """        
        res = super()._post(soft)
        for move in self:
            move._update_ref_deferred_moves()
        return res

    def _update_ref_deferred_moves(self):
        """Actualiza la referencia de los asientos diferidos con el full_voucher_name
        """        
        for move in self.filtered(
            lambda am: am.deferred_move_ids and am.name != am.full_voucher_name):

            ref = _("Deferral of %s", move.full_voucher_name or '')

            move.deferred_move_ids.write({'ref': ref})
            move.deferred_move_ids.line_ids.write({'name': ref})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
