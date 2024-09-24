# -*- encoding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import ValidationError

class AccountTax(models.Model):
    _inherit = 'account.tax'

    is_exempt = fields.Boolean('Exento')
    is_vat = fields.Boolean('IVA')
    amount_type = fields.Selection(
        selection_add=[('perception', 'Percepción'), ('retention', 'Retención')],
        ondelete={
            'perception': lambda recs: recs.write({'amount_type': 'percent', 'active': False}),
            'retention': lambda recs: recs.write({'amount_type': 'percent', 'active': False})
        }
    )
    perception_id = fields.Many2many(
        comodel_name='perception.perception',
        string='Percepción'
    )
    retention_id = fields.Many2many(
        comodel_name='retention.retention',
        string='Retención'
    )

    def _compute_amount(self, base_amount, price_unit, quantity=1.0, product=None, partner=None, fixed_multiplicator=1):
        res = super(AccountTax, self)._compute_amount(base_amount, price_unit, quantity, product, partner, fixed_multiplicator)
        if self.amount_type in ['perception', 'retention']:
            return base_amount
        return res
    
    def get_tax_by_company_and_name(self, company, name):
        if not company:
            raise ValidationError("No se especificó la empresa para buscar impuestos internos")
        if not name:
            raise ValidationError("No se especificó el nombre para buscar impuestos")
        tax = self.env['account.tax'].search([
            ('name', '=', name),
            ('company_id', '=', company.id)
        ], limit=1)
        if not tax:
            raise ValidationError(f"No se encontró el impuesto {name}")
        return tax

    def get_internal_tax_group(self, company):
        """
        TODO: Dejo esta función para que sea lo único a cambiar, pero hay varias parte del código donde estaba
        el id externo "l10n_ar.tax_group_internal" como grupo de impuesto, en v17 el grupo es por empresa y
        no hay un único id externo, para mi punto de vista habria que hacer algo como el is_vat o is_exempt,
        pero por tema de retrocompatibilidad con las versiones anteriores y tiempo prefiero dejarlo así por ahora
        """
        if not company:
            raise ValidationError("No se especificó la empresa para buscar impuestos internos")
        internal_tax = self.env['account.tax.group'].search([
            ('name', '=ilike', "impuestos internos"),
            ('company_id', '=', company.id)
        ], limit=1)
        if not internal_tax:
            raise ValidationError("No se encontró el grupo de impuestos internos")
        return internal_tax

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
