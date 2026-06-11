# -*- encoding: utf-8 -*-

from odoo import models, fields


class ResPartnerBank(models.Model):

    _inherit = 'res.partner.bank'

    cbu = fields.Char('CBU')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
