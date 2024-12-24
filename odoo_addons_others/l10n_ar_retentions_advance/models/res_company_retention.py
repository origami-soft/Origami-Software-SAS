# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class ResCompanyRetention(models.Model):
    _name = 'res.company.retention'
    _description = 'Retencion de empresa'

    @api.constrains('company_id', 'retention_id')
    def _check_repeat(self):
        for company_perception in self:
            rules = self.search([
                ('company_id', '=', company_perception.company_id.id),
                ('retention_id', '=', company_perception.retention_id.id),
                ('id', '!=', company_perception.id)
            ])
            if rules:
                raise Warning("Existe mas de una regla con retencion {}.".format(
                    company_perception.retention_id.name if company_perception.retention_id else "vacia")
                )

    retention_id = fields.Many2one(
        comodel_name='retention.retention',
        string='Retencion',
        domain="[('type_tax_use','=','purchase')]",
        check_company=True
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Empresa',
        readonly=True,
        change_default=True,
        default=lambda self: self.env.company,
    )

    state_id = fields.Many2one(
        comodel_name='res.country.state',
        string="Provincia",
        related='retention_id.state_id',
        readonly=True,
    )

    type = fields.Selection(
        selection=[
            ('vat', 'IVA'),
            ('gross_income', 'Ingresos Brutos'),
            ('profit', 'Ganancias'),
            ('other', 'Otro')
        ],
        string="Tipo",
        related='retention_id.type',
        readonly=True,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
