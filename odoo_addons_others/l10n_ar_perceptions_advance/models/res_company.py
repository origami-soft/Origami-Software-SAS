# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):

    _inherit = 'res.company'

    perception_ids = fields.One2many(
        comodel_name='res.company.perception',
        inverse_name='company_id',
        string='Percepciones',
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
