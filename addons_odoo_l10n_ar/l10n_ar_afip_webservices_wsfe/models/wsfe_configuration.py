# -*- encoding: utf-8 -*-

from odoo import models


class WsfeConfiguration(models.Model):
    _name = 'wsfe.configuration'  # Mantengo el modelo por compatibilidad, para evitar KeyError al actualizar
    _description = 'Configuración WSFE (deprecado)'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
