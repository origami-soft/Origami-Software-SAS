# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    pos_ar_id = fields.Many2one(
        comodel_name='pos.ar',
        string='Punto de venta',
        check_company=True
    )

    @api.onchange('type')
    def onchange_pos_ar_type(self):
        if self.type not in ['purchase', 'sale']:
            self.pos_ar_id = False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
