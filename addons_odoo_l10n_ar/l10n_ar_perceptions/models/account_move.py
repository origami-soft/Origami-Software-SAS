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

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    perception_ids = fields.One2many(
        'account.invoice.perception',
        'move_id',
        string='Percepciones',
        copy=True
    )
    
    def post(self):
        for r in self.filtered(lambda l: l.type.startswith('out') and l.perception_ids):
            for t in r.perception_ids.mapped('perception_id.tax_id'):
                perc = sum(r.perception_ids.filtered(lambda l: l.perception_id and l.perception_id.tax_id == t).mapped('amount'))
                line = sum(r.line_ids.filtered(lambda l: l.tax_line_id == t).mapped(lambda l: abs(l.balance if r.currency_id == r.company_id.currency_id else l.amount_currency)))
                if round(perc, 2) != round(line, 2):
                    raise ValidationError(f"Los importes declarados en {t.name} no coinciden con los de la factura.")
        return super().post()
    
    def get_perception_base(self):
        """ Obtengo la base sobre la cual voy a calcular las percepciones """
        self.ensure_one()
        return round(sum(l.price_subtotal for l in self.invoice_line_ids if l.perception_applies()), 2)
    
    def _create_perception_move_lines(self):
        """ Método auxiliar para crear los apuntes de percepciones """
        # En caso de estar dando de alta la factura en el momento, voy a crear los apuntes con new
        in_draft_mode = self != self._origin
        create_method = self.env['account.move.line'].new if in_draft_mode else self.env['account.move.line'].create
        for p in self.perception_ids:

            tax = p.perception_id.tax_id
            # En caso de que la factura sea de la misma moneda que la empresa, el apunte no lleva moneda ni importe en
            # moneda
            if self.currency_id == self.company_currency_id:
                currency_id = False
                amount_currency = 0.0
                balance = p.amount
            # Caso contrario, lleva la moneda de la factura, el importe de la percepción es el importe en moneda y el
            # convertido es el debe/haber del apunte
            else:
                currency_id = self.currency_id.id
                amount_currency = p.amount
                balance = self.currency_id._convert(p.amount, self.company_currency_id, self.company_id, self.date \
                    or fields.Date.context_today(self))

            # Defino si los impuestos van al debe o haber según el tipo de la factura
            should_be_debit = not self.is_inbound()

            # Busco las líneas de repartition para tomar la cuenta de la percepción
            tax_rep_line_field = 'refund_repartition_line_ids' if self.type.endswith('refund') \
                else 'invoice_repartition_line_ids'
            rep_lines_with_account = getattr(tax, tax_rep_line_field).filtered(lambda l: l.account_id)
            if not rep_lines_with_account:
                raise ValidationError("No ha configurado cuentas para {}".format(tax.name))
            rep_line = rep_lines_with_account[0]

            # Replico los valores con los que se arman los apuntes de impuestos regulares
            vals = {
                'amount_currency': amount_currency * (1 if should_be_debit else -1),
                'debit': should_be_debit and balance or 0.0,
                'credit': not should_be_debit and balance or 0.0,
                'tax_base_amount': p.base,
                'name': tax.name,
                'move_id': self.id,
                'company_id': self.company_id.id,
                'company_currency_id': self.company_id.currency_id.id,
                'currency_id': currency_id,
                'quantity': 1.0,
                'date_maturity': False,
                'exclude_from_invoice_tab': True,
                'tax_exigible': tax.tax_exigibility == 'on_invoice',
                'tax_repartition_line_id': rep_line.id,
                'tax_line_id': tax.id,
                'account_id': rep_line.account_id.id,
                'partner_id': self.partner_id.id,
            }

            # Me fijo si ya existe un apunte con esta percepción
            ml = self.line_ids.filtered(lambda l: l.tax_line_id == tax)
            if ml:
                ml.update(vals)
            else:
                ml = create_method(vals)
            if in_draft_mode:
                ml._onchange_amount_currency()
                ml._onchange_balance()

    def _recompute_tax_lines(self, **kwargs):
        res = super()._recompute_tax_lines(**kwargs)
        self._create_perception_move_lines()
        return res

    @api.onchange('invoice_line_ids', 'currency_id', 'currency_rate')
    def onchange_set_perception_values(self):
        if self.type in ['out_invoice', 'out_refund']:
            perc_base = self.get_perception_base()
            for perception in self.perception_ids:
                perception.base = perc_base
                perception.onchange_aliquot()
            self.onchange_perception_ids()

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.onchange_set_perception_values()
        return super()._onchange_partner_id()

    @api.onchange('perception_ids')
    def onchange_perception_ids(self):
        self.delete_perceptions()
        self.add_perceptions()
        self.with_context(check_move_validity=False)._recompute_dynamic_lines()

    def delete_perceptions(self):
        """ Para el caso que se borre una percepcion de la grilla de percepciones """
        taxes_invoices = self.invoice_line_ids.mapped('tax_ids')
        perception_taxes = self.perception_ids.mapped('perception_id').mapped('tax_id')
        taxes_to_delete = self.env['perception.perception'].search([
            ('tax_id', 'in', taxes_invoices.ids),
            ('tax_id', 'not in', perception_taxes.ids),
        ]).mapped('tax_id')
        # En caso de que haya percepciones a borrar, las saco de las líneas y marco todas las líneas que tenían alguna
        # de esas percepciones para recalcular los impuestos de las mismas
        if taxes_to_delete:
            self.invoice_line_ids.update({
                'tax_ids': [(3, perception_tax.id) for perception_tax in taxes_to_delete],
                'recompute_tax_line': True,
            })

    def add_perceptions(self):
        perception_taxes = self.perception_ids.mapped('perception_id').mapped('tax_id')
        if perception_taxes:
            # Agrego las percepciones a las líneas que correspondan y marco esas líneas para recalcular sus impuestos
            self.invoice_line_ids.filtered(lambda x: x.perception_applies()).update({
                'tax_ids': [(4, perception_tax.id) for perception_tax in perception_taxes],
                'recompute_tax_line': True,
            })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
