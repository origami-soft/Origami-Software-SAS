# -*- encoding: utf-8 -*-

from odoo import models
from odoo.exceptions import ValidationError
from l10n_ar_api.afip_webservices import wsfe, wsfex, wsbfe
import requests


SERVICE_FUNCTION = {
    'electronic_exportation': 'wsfex',
    'fiscal_electronic_bond': 'wsbfe',
    'electronic': 'wsfe'
}

TOKEN = {
    'wsfe': wsfe.wsfe.Wsfe,
    'wsfex': wsfex.wsfex.Wsfex,
    'wsbfe': wsbfe.wsbfe.Wsbfe,
}


class DocumentBook(models.Model):

    _inherit = 'document.book'

    def action_wsfe_number(self, afip_wsfe, document_afip_code):
        """
        Valida que el ultimo numero del talonario sea el correcto en comparacion con el de la AFIP.
        :param afip_wsfe: instancia Wsfe.
        :param document_afip_code: Codigo de afip del documento.
        """
        default_cipher = requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'AES128-SHA'
        try:
            last_number = str(afip_wsfe.get_last_number(self.pos_ar_id.name, document_afip_code))
        except Exception as e:
            raise ValidationError(e.args)
        finally:
            requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = default_cipher

        if last_number.zfill(8) != self.last_number.zfill(8):
            raise ValidationError('El ultimo numero del talonario ({0}) no coincide con el de la AFIP ({1})'.format(
                self.last_number, last_number))

    def set_last_number_of_book_from_afip(self):
        # TODO: Estaria bueno usar esta nueva funcion para los envios a afip de cada tipo
        service_type = SERVICE_FUNCTION.get(self.book_type_id.type)
        if service_type:
            wsaa_token = self.env['wsaa.token'].search([
                ('name', '=', service_type),
                ('wsaa_configuration_id.company_id', '=', self.company_id.id),
            ], limit=1)
            if not wsaa_token:
                raise ValidationError("No se encontró token para la empresa {} y el servicio {}".format(
                    self.company_id.name, service_type
                ))
            access_token = wsaa_token.get_access_token()
            homologation = False if wsaa_token.wsaa_configuration_id.type == 'production' else True

            default_cipher = requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS
            requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'AES128-SHA'
            try:
                service = TOKEN.get(service_type)(access_token, self.company_id.vat, homologation)
                service.check_webservice_status()
                self.last_number = service.get_last_number(self.pos_ar_id.name, self.voucher_type_id.code)
            finally:
                requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = default_cipher

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
