# - coding: utf-8 -*-

from odoo import models, fields, api


class UpdateBanksWizard(models.TransientModel):
    _name = 'update.banks.wizard'
    _description = 'Wizard de actualización de bancos'

    name = fields.Char()

    def action_update(self):
        self.env['res.bank'].update_banks()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
