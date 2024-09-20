# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class AccountTaxAr(models.AbstractModel):
    _name = 'account.tax.ar'
    _description = 'Impuesto de argentina'

    def _get_country_ar(self):
        return [('country_id', '=', self.env.ref('base.ar').id)]

    name = fields.Char(
        string='Nombre',
        required=True
    )
    type = fields.Selection(
        [
            ('vat', 'Iva'),
            ('gross_income', 'Ingresos brutos'),
            ('profit', 'Ganancias'),
            ('other', 'Otro')
        ],
        string='Tipo',
        required=True,
        default='gross_income'
    )
    type_tax_use = fields.Selection(
        [('sale', 'Ventas'),
         ('purchase', 'Compras'),
         ('none', 'Ninguna')],
    )
    jurisdiction = fields.Selection(
        [
            ('nacional', 'Nacional'),
            ('provincial', 'Provincial'),
            ('municipal', 'Municipal')
        ],
        string='Jurisdiccion',
        required=True,
        default='nacional'
    )
    state_id = fields.Many2one(
        'res.country.state',
        string="Provincia",
        domain=_get_country_ar
    )
    company_id = fields.Many2one(
        'res.company',
        string='Compania',
        default=lambda self: self.env.company,
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

    def get_taxes(self, company):
        raise NotImplementedError("Método no implementado")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
