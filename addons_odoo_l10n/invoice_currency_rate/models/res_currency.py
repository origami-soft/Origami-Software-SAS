# -*- encoding: utf-8 -*-

from odoo import models, fields


class ResCurrency(models.Model):

    _inherit = 'res.currency'

    need_rate = fields.Boolean(
        string='¿Lleva cotización?',
        copy=False
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
