# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountDocumentTax(models.AbstractModel):
    _name = 'account.document.tax'
    _description = 'Impuesto abstracto'

    currency_id = fields.Many2one('res.currency')
    amount = fields.Monetary('Importe', currency_field='currency_id', required=True)
    base = fields.Monetary('Base', currency_field='currency_id')
    aliquot = fields.Float('Alicuota')
    name = fields.Char('Nombre', required=True)

    @api.constrains('amount')
    def check_amount(self):
        for tax in self:
            if tax.amount <= 0:
                raise ValidationError('El monto del impuesto debe ser mayor a 0')

    @api.constrains('base')
    def check_base(self):
        for tax in self:
            if tax.base < 0:
                raise ValidationError('La base del impuesto no puede ser negativa')

    @api.constrains('aliquot')
    def check_aliquot(self):
        for tax in self:
            if tax.aliquot < 0 or tax.aliquot > 100:
                raise ValidationError('La alicuota no puede ser menor que 0% o mayor que 100%')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
