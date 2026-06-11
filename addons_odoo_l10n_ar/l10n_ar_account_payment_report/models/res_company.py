# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    customer_receipt_print_option = fields.Selection([
        ('docs_imputed', 'Documentos Imputados'),
        ('docs_to_impute', 'Documentos a Imputar'),
    ], string='Imprimir en recibos de cliente',
       default='docs_imputed',
       help='Seleccione qué solapa se imprimirá en los recibos de cliente.',
       required=True
    )
    customer_receipt_print_option_last_update = fields.Datetime(
        string='Última modificación',
        readonly=True,
    )
    customer_receipt_print_option_last_user_id = fields.Many2one(
        'res.users',
        string='Última modificación por',
        readonly=True,
    )

    def write(self, vals):
        # Registrar fecha/hora y usuario de última modificación cuando se cambia el campo
        if 'customer_receipt_print_option' in vals:
            vals['customer_receipt_print_option_last_update'] = fields.Datetime.now()
            vals['customer_receipt_print_option_last_user_id'] = self.env.uid
        return super(ResCompany, self).write(vals)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
