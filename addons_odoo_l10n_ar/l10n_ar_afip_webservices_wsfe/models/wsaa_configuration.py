# -*- encoding: utf-8 -*-

from odoo import models
from odoo.exceptions import ValidationError
from l10n_ar_api.afip_webservices import wsfe, wsfex, wsbfe
from requests.exceptions import HTTPError
import requests


class WsaaConfiguration(models.Model):
    _inherit = 'wsaa.configuration'

    def get_wsfe(self, company):
        """
        Busca el objeto de wsfe para utilizar sus servicios
        :return: instancia de Wsfe
        """
        wsfe_token = self.env['wsaa.token'].search([
            ('name', '=', 'wsfe'),
            ('wsaa_configuration_id.company_id', '=', company.id),
        ], limit=1)

        if not wsfe_token:
            raise ValidationError('No se encontró ningún token de factura electrónica')

        access_token = wsfe_token.get_access_token()
        homologation = False if wsfe_token.wsaa_configuration_id.type == 'production' else True
        default_cipher = requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'AES128-SHA'
        try:
            return wsfe.wsfe.Wsfe(access_token, company.vat, homologation)
        except HTTPError as e:
            if hasattr(e, 'response') and hasattr(e.response, 'status_code') and e.response.status_code >= 500:
                raise ValidationError("El servidor de AFIP no se encuentra disponible. Intente más tarde.")
            raise e
        finally:
            requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = default_cipher
    
    def get_wsfex(self, company, partner=False):
        """
        Busca el objeto de wsfex para utilizar sus servicios
        :return: instancia de Wsfex
        """
        wsfex_token = self.env['wsaa.token'].search([
            ('name', '=', 'wsfex'),
            ('wsaa_configuration_id.company_id', '=', company.id),
        ], limit=1)

        if not wsfex_token:
            raise ValidationError('No se encontró ningún token de factura electrónica de exportación')

        foreign_fiscal_positions = [
            self.env.ref('l10n_ar_bo.ar_fiscal_position_cliente_ext'),
            self.env.ref('l10n_ar_bo.ar_fiscal_position_prov_ext'),
        ]
        
        if partner:
            is_foreign = partner.property_account_position_id.ar_fiscal_position_id in foreign_fiscal_positions

            if not partner.vat and not is_foreign:
                raise ValidationError("El partner {} no posee número de documento.".format(partner.name))

            if not partner.country_id.vat and is_foreign and partner.country_id != self.env.ref('base.ar'):
                raise ValidationError("El partner {} no posee país con documento.".format(partner.name))

        access_token = wsfex_token.get_access_token()
        homologation = False if wsfex_token.wsaa_configuration_id.type == 'production' else True
        default_cipher = requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'AES128-SHA'
        try:
            return wsfex.wsfex.Wsfex(access_token, company.vat, homologation)
        except HTTPError as e:
            if hasattr(e, 'response') and hasattr(e.response, 'status_code') and e.response.status_code >= 500:
                raise ValidationError("El servidor de AFIP no se encuentra disponible. Intente más tarde.")
            raise e
        finally:
            requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = default_cipher

    def get_wsbfe(self, company):
        """
        Busca el objeto de wsbfe para utilizar sus servicios
        :return: instancia de Wsbfe
        """
        wsbfe_token = self.env['wsaa.token'].search([
            ('name', '=', 'wsbfe'),
            ('wsaa_configuration_id.company_id', '=', company.id),
        ], limit=1)

        if not wsbfe_token:
            raise ValidationError('No se encontró ningún token de bono fiscal electrónico')

        access_token = wsbfe_token.get_access_token()
        homologation = False if wsbfe_token.wsaa_configuration_id.type == 'production' else True
        default_cipher = requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'AES128-SHA'
        try:
            return wsbfe.wsbfe.Wsbfe(access_token, company.vat, homologation)
        except HTTPError as e:
            if hasattr(e, 'response') and hasattr(e.response, 'status_code') and e.response.status_code >= 500:
                raise ValidationError("El servidor de AFIP no se encuentra disponible. Intente más tarde.")
            raise e
        finally:
            requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = default_cipher

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
