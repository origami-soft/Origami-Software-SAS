# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class VoucherType(models.Model):
    _inherit = 'voucher.type'

    category = fields.Selection(
        selection_add=[
            ('invoice', 'Factura'),
            ('refund', 'Nota de crédito'),
            ('payment_out', 'Pago'),
            ('payment_in', 'Cobro')
        ],
        ondelete={'invoice': 'cascade', 
        'refund': 'cascade', 
        'payment_out': 'cascade', 
        'payment_in': 'cascade',}
    )
    refund_voucher_type_id = fields.Many2one(
        comodel_name='voucher.type', 
        string='Documento de devolución'
    )

    active = fields.Boolean(
        string='Activo',
        default=True
    )

    @api.model
    def unlink(self):
        for record in self:
            record.active = False
        return True

    @api.depends('prefix', 'name')
    def _compute_display_name(self):
        for r in self:
            r.display_name = '({}) {}'.format(r.prefix, r.name) if r.prefix else r.name
    
    def get_domain_available_voucher_types(self, params):
        domain = [('category', '=', params.get('category'))]
        if 'denomination_ids' in params:
            domain.append(('denomination_id', 'in', params.get('denomination_ids')))
        return domain
    
    def get_available_voucher_types(self, params):
        domain = self.get_domain_available_voucher_types(params)
        return self.sudo().search(domain)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
