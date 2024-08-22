# -*- encoding: utf-8 -*-

from odoo import models, fields


class AccountAbstractCheck(models.AbstractModel):
    _inherit = 'account.abstract.check'

    reject_move_id = fields.Many2one('account.move', 'Asiento de rechazo')
    reject_date = fields.Date('Fecha de rechazo')

    def create_reject_move(self, move_date):
        """ Crea el asiento de rechazo de cheques """
        vals = self.get_reject_move_vals(move_date)
        move = self.env['account.move'].create(vals)
        move.action_post()
        self.write({
            'reject_move_id': move.id,
            'reject_date': move_date,
        })

    def get_reject_move_vals(self):
        """ Función que se hereda por cheque propio y de terceros """
        raise NotImplementedError()

    def get_reject_check_wizard(self):
        return {
            'name': "Rechazar Cheque",
            'type': 'ir.actions.act_window',
            'res_model': 'reject.checks.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
