# -*- encoding: utf-8 -*-

from odoo import models, fields


class PosAr(models.Model):

    _inherit = 'pos.ar'

    invoicing_address_id = fields.Many2one(
        'res.partner',
        'Dirección de facturación',
        help='Se utilizará la dirección de este partner en las facturas electrónicas'
    )
    invoice_logo = fields.Binary(
        string="Logo factura electrónica",
        help="El logo que saldrá en las facturas electrónicas de este punto de venta."
    )
    invert_colors_qr = fields.Boolean(
        string="Invertir Colores QR",
        help="Utilice este campo para invertir los colores del QR en caso de que salga al revez.",
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
