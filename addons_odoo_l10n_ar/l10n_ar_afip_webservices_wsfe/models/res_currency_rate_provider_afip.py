# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
from odoo import fields, models
import requests


class ResCurrencyRateProviderAFIP(models.Model):
    _inherit = "res.currency.rate.provider"

    service = fields.Selection(
        selection_add=[("AFIP", "Administración Federal de Ingresos Públicos")],
        ondelete={"AFIP": "set default"},
    )

    def _get_supported_currencies(self):
        self.ensure_one()
        if self.service != "AFIP":
            return super()._get_supported_currencies()
        currency_ids = self.env['codes.models.relation'].search([
            ('name', '=', 'Afip'),
            ('name_model', '=', 'res.currency'),
        ]).mapped('id_model')
        return self.env['res.currency'].browse(currency_ids).exists().mapped('name')

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
        if self.service != "AFIP":
            return super()._obtain_rates(
                base_currency, currencies, date_from, date_to
            )

        currency_ids = self.env['res.currency'].search([('name', 'in', currencies)])
        rates = {}
        for currency in currency_ids:
            rate = self.get_cotization_from_afip(currency, self.company_id)
            rates[currency.name] = 1/rate
        content[date_to] = rates
        return content
    
    def get_cotization_from_afip(self, currency, company):
        currency_code = self.env['codes.models.relation'].get_code(
            'res.currency',
            currency.id,
            'Afip'
        )
        wsfe = self.env['wsaa.configuration'].get_wsfe(company)
        try:
            default_cipher = requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS
            requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'AES128-SHA'
            cotiz = wsfe.get_cotization(currency_code)
        except Exception as e:
            raise ValidationError(e.args)
        finally:
                requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = default_cipher
        return cotiz

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
