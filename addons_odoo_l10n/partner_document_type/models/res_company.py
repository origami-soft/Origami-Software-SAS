# -*- encoding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    partner_document_type_id = fields.Many2one(
        comodel_name='partner.document.type',
        related='partner_id.partner_document_type_id',
        string='Tipo de documento'
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
