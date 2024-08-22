# -*- encoding: utf-8 -*-

from odoo import models, fields

class StockPicking(models.Model):

    _inherit = "stock.picking"

    dispatch_number = fields.Char(
        string="Número de Despacho",
        help='Si define un número de despacho, al validar la transferencia, '
        'el mismo será asociado a los lotes sin número de despacho vinculados '
        'a la transferencia.'
    )

    def _action_done(self):
        res = super()._action_done()
        for rec in self.filtered(lambda x: x.picking_type_code == 'incoming' and x.dispatch_number):
            for line in rec.move_line_ids.filtered(lambda l: l.lot_id).mapped('lot_id'):
                if line.dispatch_number:
                    line.dispatch_number += ', ' + rec.dispatch_number
                    continue
                line.dispatch_number = rec.dispatch_number
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
