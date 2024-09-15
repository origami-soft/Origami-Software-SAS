# -*- coding: utf-8 -*-

from odoo import fields, models
from .bna_service import BNAService


class ResCurrencyRateProviderBNA(models.Model):
    _inherit = "res.currency.rate.provider"

    service = fields.Selection(
        selection_add=[("BNA", "Banco de la Nación Argentina"),("BNA-DIV", "Banco de la Nación Argentina - DIVISA")],
        ondelete={"BNA": "set default", "BNA-DIV": "set default"},
    )

    def _get_supported_currencies(self):
        self.ensure_one()
        if self.service == "BNA":
            return ['USD', 'EUR']
        if self.service == "BNA-DIV":
            return ['USD', 'EUR', 'GBP']
        return super()._get_supported_currencies()

    def _obtain_rates(self, base_currency, currencies, date_from, date_to):
        """
        Obtiene las tasas de cambio de moneda desde un proveedor externo para un rango de fechas específico.
        
        La función devuelve un diccionario que contiene las tasas de cambio para cada fecha y moneda objetivo.
        La clave del diccionario es la fecha en formato de cadena (YYYY-MM-DD) y el valor es otro diccionario que
        contiene las tasas de cambio para cada moneda objetivo con respecto a la moneda base.
        
        Ejemplo de retorno:
        {
            '2023-06-01': {
                'EUR': 0.85,
                'GBP': 0.73,
            },
            '2023-06-02': {
                'EUR': 0.86,
                'GBP': 0.74,
            },
            ...
        }
        """
        self.ensure_one()
        content = {}
        if self.service != "BNA" and self.service != "BNA-DIV":
            return super()._obtain_rates(
                base_currency, currencies, date_from, date_to
            )
        rates = {}
        for currency in currencies:
            service = BNAService(currency)
            moneda = service.get_cotization_from_bna(service=self.service)
            rates[currency] = 1/moneda.get('value')
        content[date_to] = rates
        return content

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
