# -*- encoding: utf-8 -*-

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _compute_all_tax(self):
        for m in self.mapped('move_id'):
            lines = self.filtered(lambda l: l.move_id == m)
            perception_calculated_lines = self.env['account.move.line']
            accumulated_perceptions = {}
            direction_sign = m.direction_sign
            for l in lines:
                # En caso de que la línea actual aplique percepción, la guardo en un recordset así sé cuándo calculé
                # percepciones para todas las líneas percibibles de la factura
                if l.perception_applies():
                    perception_calculated_lines |= l
                # Calculo el signo que compute_all va a aplicar internamente al resultado de _compute_amount,
                # para poder ajustar correctamente el importe de la última línea percibible
                if l.display_type == 'product' and l.move_id.is_invoice(True):
                    base_for_sign = direction_sign * l.price_unit * (1 - l.discount / 100) * l.quantity
                else:
                    base_for_sign = l.amount_currency
                compute_all_sign = -1 if base_for_sign < 0 else 1
                l = l.with_context({
                    'perception_ctx': m.get_perception_ctx(),
                    'perception_calculated_lines': perception_calculated_lines,
                    'accumulated_perceptions': accumulated_perceptions,
                    'compute_all_sign': compute_all_sign,
                })
                super(AccountMoveLine, l)._compute_all_tax()
                for k, v in l.compute_all_tax.items():
                    if k.get('tax_repartition_line_id'):
                        tax = self.env['account.tax.repartition.line'].browse(k['tax_repartition_line_id']).tax_id
                        if tax.amount_type == 'perception':
                            if not accumulated_perceptions.get(tax):
                                accumulated_perceptions[tax] = 0.0
                            accumulated_perceptions[tax] += v.get('amount_currency', 0.0)

    def perception_applies(self):
        self.ensure_one()
        return self.product_id and self.product_id.perception_taxable\
            or not (self.product_id or self.display_type in ('line_section', 'line_note'))

    def _compute_totals(self):
        self = self.with_context(skip_perceptions=True)
        return super()._compute_totals()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
