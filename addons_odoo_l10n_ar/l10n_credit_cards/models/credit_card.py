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
