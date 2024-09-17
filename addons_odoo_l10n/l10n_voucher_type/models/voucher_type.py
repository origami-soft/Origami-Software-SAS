# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class VoucherType(models.Model):
    _name = 'voucher.type'
    _description = 'Tipos de comprobantes'
    _order = 'code asc'

    name = fields.Char(
        string='Nombre', 
        required=True
    )
    prefix = fields.Char(string='Prefijo')
    category = fields.Selection(
        selection=[('none', 'Ninguna')], 
        string='Categoría', 
        required=True
    )
    code = fields.Integer(string='Código')
    active = fields.Boolean(
        string='Activo', 
        default=True
    )
    is_debit_note = fields.Boolean(string='Nota de débito')

    @api.model
    def unlink(self):
        for record in self:
            record.active = False
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
