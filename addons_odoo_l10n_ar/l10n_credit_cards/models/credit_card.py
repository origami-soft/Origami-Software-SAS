# -*- encoding: utf-8 -*-

from odoo import models, fields


class CreditCard(models.Model):
    _name = 'credit.card'
    _description = 'Tarjeta de crédito'

    name = fields.Char(
        string='Nombre',
        required=True
    )
    type = fields.Selection(
        selection=[('purchase', 'Compras'), ('sale', 'Ventas')],
        string='Tipo',
        required=True
    )
    active = fields.Boolean(
        string='Activo',
        default=True
    )

    def get_default_journal(self):
        """ Se obtiene el diario por defecto desde la configuracion de la compañia"""
        journal = self.env.company.credit_card_journal_id
        return journal or False

    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Diario',
        required=True,
        default=get_default_journal
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Empresa',
        default=lambda self: self.env.company,
    )
    plan_ids = fields.One2many(
        comodel_name='credit.card.payment.plan',
        string='Planes de pago',
        inverse_name='credit_card_id',
    )

    _sql_constraints = [('unique_name', 'unique(name, company_id)', 'Ya existe una tarjeta con ese nombre')]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
