# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    cai = fields.Char("CAI", copy=False)
    cai_due_date = fields.Date("Fecha vencimiento CAI", copy=False)
    voucher_name = fields.Char(
        'Numero documento',
        copy=False
    )
    internal_number = fields.Char(
        'Numero interno',
        copy=False
    )

    def update_move_names(self):
        self.ensure_one()
        self.env['stock.move'].search([('picking_id', '=', self.id)]).write({'reference': self.name})

    def set_picking_number(self, document_book):
        self.ensure_one()
        if not self.voucher_name:
            self.voucher_name = '{}-{}'.format(
                document_book.pos_ar_id.name.zfill(document_book.pos_ar_id.prefix_quantity or 0),
                document_book.next_number()
            )
        picking_name = '{}{}'.format(
            document_book.voucher_type_id.prefix + ' ' if document_book.voucher_type_id.prefix else '',
            self.voucher_name
        )
        self.update({
            'internal_number': picking_name != self.name and self.name,
            'name': picking_name
        })
        self.update_move_names()

    def action_done(self):
        res = super(StockPicking, self).action_done()
        for r in self:
            r.action_done_picking_number()
        return res

    def action_done_picking_number(self):
        self.ensure_one()
        document_book = self.picking_type_id.get_document_book(self.company_id)
        if document_book:
            self.set_picking_number(document_book)
            if document_book.book_type_id.type == 'selfprint':
                self.picking_type_id.validate_cai_fields(document_book)
                self.update({
                    'cai': document_book.cai,
                    'cai_due_date': document_book.cai_due_date,
                })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
