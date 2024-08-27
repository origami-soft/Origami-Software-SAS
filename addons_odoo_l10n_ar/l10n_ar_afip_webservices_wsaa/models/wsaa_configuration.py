# -*- encoding: utf-8 -*-

from odoo import models, fields
from l10n_ar_api.afip_webservices.wsaa import certificate
from odoo.exceptions import ValidationError


class WsaaConfiguration(models.Model):

    _name = 'wsaa.configuration'
    _description = 'Configuración wsaa'

    name = fields.Char('Nombre', required=True)
    type = fields.Selection([
            ('homologation', 'Homologacion'),
            ('production', 'Produccion')
        ],
        'Tipo',
        required=True
    )
    private_key = fields.Text('Llave privada')
    certificate_request = fields.Text('Pedido de certificado')
    certificate = fields.Text('Certificado')
    wsaa_token_ids = fields.One2many('wsaa.token', 'wsaa_configuration_id', 'Tokens')
    company_id = fields.Many2one(
        'res.company',
        'Empresa',
        required=True,
        default=lambda self: self.env.company
    )

    def generate_certificate_request(self):
        """ Genera un nuevo pedido de certificado con la key configurada """

        if not self.private_key:
            raise ValidationError("Falta configurar la clave privada")

        # Seteamos los valores necesarios para la generacion del pedido de certificado
        req = certificate.WsaaCertificate(self.private_key)
        req.country_code = self.company_id.country_id.code
        req.state_name = self.company_id.state_id.name
        req.company_name = self.company_id.name

        if self.company_id.partner_id.vat:
            req.company_vat = 'CUIT {cuit}'.format(cuit=self.company_id.partner_id.vat)
        try:
            certificate_request = req.generate_certificate_request(),
        except AttributeError as e:
            raise ValidationError(e.args)

        self.write({
            'certificate_request': certificate_request[0],
            'certificate': None
        })

    def generate_private_key(self):
        """ Genera una nueva clave privada y borra los parametros de configuacion viejos """

        pk = certificate.WsaaPrivateKey()
        pk.generate_rsa_key()
        self.write({
            'private_key': pk.key,
            'certificate_request': None,
            'certificate': None
        })


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
