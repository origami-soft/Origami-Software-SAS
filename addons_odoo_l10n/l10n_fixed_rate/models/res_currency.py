# -*- encoding: utf-8 -*-

from odoo import models


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    def _get_conversion_rate(self, from_currency, to_currency, company, date):
        """
        Heredo la función que trae las tasas de conversión para que, en caso de que se haya pasado por contexto una
        cotización fija y la moneda de dicha cotización fija sea una de las cuales se irán a buscar cotizaciones a la
        base de datos, se devuelva dicha cotización
        """
        ctx = self.env.context
        if ctx.get('fixed_rate'):
            if from_currency == ctx['fixed_from_currency'] and to_currency == ctx['fixed_to_currency']:
                return ctx['fixed_rate']
            if from_currency == ctx['fixed_to_currency'] and to_currency == ctx['fixed_from_currency']:
                return 1 / ctx['fixed_rate']
        return super(ResCurrency, self)._get_conversion_rate(from_currency, to_currency, company, date)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
