# -*- encoding: utf-8 -*-

from odoo import models


class AccountTax(models.Model):
    _inherit = 'account.tax'

    def _compute_amount(self, base_amount, price_unit, quantity=1.0, product=None, partner=None, fixed_multiplicator=1):
        """ En caso de estar calculando una percepción, devuelvo el importe de la percepción prorrateado según la base """
        if self.amount_type == 'perception':
            if self.env.context.get('skip_perceptions'):
                return 0
            # En caso de estar calculando percepciones para los apuntes, hago un cálculo prorrateando en base a las
            # líneas de la factura
            perception_ctx = self.env.context.get('perception_ctx', {})
            if perception_ctx:
                return self._compute_perception_amount_for_move_line(base_amount, perception_ctx)
            # En caso de estar calculando percepciones para el visor de totales, directamente tomo el importe declarado
            # en la grilla
            totals_perception_ctx = self.env.context.get('totals_perception_ctx', {})
            if totals_perception_ctx:
                return self._compute_perception_amount_for_totals(totals_perception_ctx)
        return super()._compute_amount(base_amount, price_unit, quantity, product, partner, fixed_multiplicator)

    def _compute_perception_amount_for_move_line(self, base_amount, perception_ctx):
        perception_base = perception_ctx.get('base', 0)
        if not perception_base:
            return 0

        accumulated = self.env.context.get('accumulated_perceptions', {})
        # Tomo el importe total de la percepción desde el contexto, tal cual figura en la grilla
        perception_value = perception_ctx.get(self, 0) or perception_ctx.get(self._origin, 0)
        accumulated_val = accumulated.get(self, 0) or accumulated.get(self._origin, 0)

        perception_calculated_lines = self.env.context['perception_calculated_lines']

        invoice = perception_ctx['invoice']
        # Si estoy calculando percepciones para la última línea, tomo como importe a calcular lo que reste para llegar
        # al importe de la percepción, así me aseguro que los totales van a ser iguales.
        # Se tiene en cuenta el direction_sign (signo de la factura) y el compute_all_sign (signo que compute_all
        # aplica internamente al resultado) para que el ajuste de redondeo funcione correctamente cuando hay líneas
        # con signos mixtos (ej: cupones de descuento en una factura de venta).
        if perception_calculated_lines == invoice.invoice_line_ids.filtered(lambda l: l.perception_applies()):
            direction_sign = perception_ctx.get('direction_sign', 1)
            compute_all_sign = self.env.context.get('compute_all_sign', 1)
            amount = (direction_sign * perception_value - accumulated_val) / compute_all_sign
        # Si aún faltan percepciones por calcular, tomo como importe a calcular el proporcional de la línea actual
        # sobre el importe de la percepción
        else:
            amount = perception_value * base_amount / perception_base

        return amount

    def _compute_perception_amount_for_totals(self, totals_perception_ctx):
        return totals_perception_ctx.pop(self, 0) or totals_perception_ctx.pop(self._origin, 0)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
