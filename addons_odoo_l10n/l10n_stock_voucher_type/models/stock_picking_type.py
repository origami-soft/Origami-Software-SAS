# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    pos_ar_ids = fields.Many2many('pos.ar', string="Puntos de venta")

    def get_document_book(self, company):
        self.ensure_one()
        pos_ar_id = self.pos_ar_ids.filtered(lambda l: l.company_id == company)
        if not pos_ar_id:
            return False
        pos_ar_id = pos_ar_id[0]
        domain = ([
            ('pos_ar_id', '=', pos_ar_id.id),
            ('category', '=', 'picking'),
        ])
        document_book = self.env['document.book'].search(domain, limit=1)
        if not document_book:
            raise ValidationError(
                'No existe talonario configurado para el punto de venta ' + pos_ar_id.display_name
            )
        return document_book

    @api.onchange('code')
    def onchange_code_clear_pos(self):
        self.pos_ar_ids = False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
