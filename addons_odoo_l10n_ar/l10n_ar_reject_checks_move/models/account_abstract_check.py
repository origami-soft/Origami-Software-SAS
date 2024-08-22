# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields


class AccountAbstractCheck(models.AbstractModel):
    _inherit = 'account.abstract.check'

    reject_move_id = fields.Many2one('account.move', 'Asiento de Rechazo')

    def create_reject_move(self):
        """ Crea el asiento de rechazo de cheques """
        vals = self.get_reject_move_vals()
        move = self.env['account.move'].create(vals)
        move.post()
        self.reject_move_id = move

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
