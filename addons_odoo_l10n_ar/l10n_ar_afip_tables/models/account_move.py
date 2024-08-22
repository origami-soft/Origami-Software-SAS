# -*- encoding: utf-8 -*-

from odoo import models, fields


class AccountMove(models.Model):

    _inherit = 'account.move'
            
    afip_concept_id = fields.Many2one('afip.concept', 'Concepto', copy=False)
    retention_legend = fields.Boolean("Leyenda de retención", copy=False)
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
