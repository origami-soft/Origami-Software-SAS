# -*- encoding: utf-8 -*-

from odoo import models


class AccountTax(models.Model):
    _inherit = 'account.tax'

    def _compute_amount(self, base_amount, price_unit, quantity=1.0, product=None, partner=None, fixed_multiplicator=1):
        """ En caso de estar calculando una percepción, devuelvo 0 porque voy a generar el apunte por fuera (salvo que
        esté actualizando el widget de totales, en cuyo caso devuelvo el valor de la percepción en sí)
        """
        if self.amount_type == 'perception':
            perception_value = self.env.context.get('perception_ctx', {}).get(self, 0) or self.env.context.get('perception_ctx', {}).get(self._origin, 0)
            # En caso de que la percepción esté dentro del contexto, la saco para que no se vuelva a calcular de nuevo
            # en las líneas siguientes
            if perception_value:
                ctx = self.env.context.copy()
                if ctx['perception_ctx'].get(self, False):
                    del ctx['perception_ctx'][self]
                else:
                    del ctx['perception_ctx'][self._origin]
                self = self.with_context(ctx)
            return perception_value
        return super()._compute_amount(base_amount, price_unit, quantity, product, partner, fixed_multiplicator)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
