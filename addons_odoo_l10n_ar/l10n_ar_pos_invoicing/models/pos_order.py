# -*- coding: utf-8 -*-

from odoo import models


class PosOrder(models.Model):
    _inherit = "pos.order"

    def _create_invoice(self, move_vals):
        res = super(PosOrder, self)._create_invoice(move_vals)
        # Hace commit al crear una factura desde POS, ya que los métodos que envían a AFIP validan que esté en la base, y si se valida inmediatamente después va a romper.
        if res.pos_ar_id:
            self.env.cr.commit()
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
