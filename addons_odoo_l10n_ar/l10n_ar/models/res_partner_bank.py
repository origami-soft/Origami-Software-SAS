# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class ResPartnerBank(models.Model):

    _inherit = 'res.partner.bank'

    cbu = fields.Char('CBU')

    active = fields.Boolean(
        string='Activo',
        default=True
    )

    @api.model
    def unlink(self):
        for record in self:
            record.active = False
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
