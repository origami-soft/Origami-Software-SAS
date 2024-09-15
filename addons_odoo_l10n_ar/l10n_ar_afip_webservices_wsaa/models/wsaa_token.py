# -*- encoding: utf-8 -*-

import pytz
from odoo import models, fields
from datetime import datetime, timedelta
from dateutil.parser import isoparse
from l10n_ar_api.afip_webservices import wsaa
from odoo.exceptions import ValidationError
from odoo import SUPERUSER_ID
from odoo import registry


class WsaaToken(models.Model):

    _name = 'wsaa.token'
    _description = 'Token wsaa'

    name = fields.Char('Servicio', required=True)
    expiration_time = fields.Datetime('Fecha de expiracion')
    token = fields.Text('Token', readonly=True)
    sign = fields.Text('Sign', readonly=True)
    wsaa_configuration_id = fields.Many2one(
        'wsaa.configuration',
        'Configuracion',
        required=True,
        check_company=True
    )
    company_id = fields.Many2one(
        'res.company',
        string='Compania',
        related='wsaa_configuration_id.company_id',
        store=True,
        readonly=True,
        related_sudo=False
    )

    def get_access_token(self):
        """
        Crea el objeto de ticket de acceso para utilizar en el los webervices
        :return: instancia de AcessToken
        """
        self.ensure_one()

        return self.action_renew()

    def action_renew(self, context=None, delta_time_for_expiration=10):
        """ Renueva o crea el ticket de acceso si esta vencido o no creado """

        self.ensure_one()

        renew = True
        if self.expiration_time:

            # Si faltan mas de X minutos para que el ticket expire no se lo renueva
            if datetime.now() + timedelta(minutes=delta_time_for_expiration) < self.expiration_time:
                renew = False

        if renew:
            token = self._renew_ticket()
            with registry(self.env.cr.dbname).cursor() as new_cr:
                self = self.with_env(self.env(cr=new_cr))
                self.sudo().write({
                    'expiration_time': isoparse(token.expiration_time).replace(tzinfo=None),
                    'token': token.token,
                    'sign': token.sign,
                })
                new_cr.commit()

        data = {
            'sign': token.sign if renew else self.sign,
            'token': token.token if renew else self.token,
        }
        access_token = wsaa.tokens.AccessToken()
        access_token.sign = data.get('sign')
        access_token.token = data.get('token')

        return access_token


    def _renew_ticket(self):
        """ Renueva o crea el ticket de acceso si esta vencido o no creado """

        if not (self.wsaa_configuration_id.certificate and self.wsaa_configuration_id.private_key):
            raise ValidationError("Falta configurar certificado o clave privada")

        # Traemos el timezone
        user = self.env['res.users'].sudo().browse(SUPERUSER_ID)
        tz = pytz.timezone(user.partner_id.tz) if user.partner_id.tz else pytz.utc

        # Creamos el token nuevo para el servicio especificado y lo firmamos con la clave y certificado
        token = wsaa.tokens.AccessRequerimentToken(self.name, tz)
        homologation = False if self.wsaa_configuration_id.type == 'production' else True
        try:
            signed_tra = token.sign_tra(self.wsaa_configuration_id.private_key, self.wsaa_configuration_id.certificate)
            # Hacemos el logeo y obtenemos sus datos
            login_fault = wsaa.wsaa.Wsaa(homologation).login(signed_tra)
        except Exception as e:
            raise ValidationError(e.args)

        access_token = wsaa.tokens.AccessToken()
        access_token.create_token_from_login(login_fault)

        return access_token

    _sql_constraints = [('unique_token_service', 'unique(name, company_id)', 'Ya existe un token para este servicio')]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
