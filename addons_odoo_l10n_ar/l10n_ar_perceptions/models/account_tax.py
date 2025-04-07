# -*- encoding: utf-8 -*-

from odoo import models


class AccountTax(models.Model):
    _inherit = 'account.tax'

    def _compute_amount(self, base_amount, price_unit, quantity=1.0, product=None, partner=None, fixed_multiplicator=1):
        """ En caso de estar calculando una percepción, devuelvo el proporcional de la percepción contra la base de la
        factura según el campo base_amount
        """
        if self.amount_type == 'perception':
            perception_base = self.env.context.get('perception_ctx', {}).get('base', 0)
            if not perception_base:
                return 0
            perception_value = self.env.context.get('perception_ctx', {}).get(self, 0) or self.env.context.get('perception_ctx', {}).get(self._origin, 0)
            return base_amount * perception_value / perception_base
        return super()._compute_amount(base_amount, price_unit, quantity, product, partner, fixed_multiplicator)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
