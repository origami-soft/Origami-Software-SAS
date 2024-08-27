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
from odoo.exceptions import ValidationError


class RejectChecksWizard(models.TransientModel):

    _name = 'reject.checks.wizard'
    _description = 'Rechazo de Cheques Wizard'

    create_moves = fields.Boolean(string='Generar Asientos?')
    check_state = fields.Selection([
        ('draft', 'Borrador'),
        ('sold', 'Vendido'),
        ('handed', 'Entregado'),
        ('wallet', 'En cartera'),
        ('collect', 'Cobrado'),
        ('deposited', 'Depositado')
    ],  string='Estado'
    )

    def reject_check_wizard(self):
        check_id = self.env.context.get('active_id')
        model = self.env.context.get('active_model')
        check = self.env[model].browse(check_id)
        if self.create_moves and check.reject_move_id:
            raise ValidationError("El cheque contiene el asiento {} generado en un rechazo anterior. "
                                  "Por favor eliminelo antes de volver a rechazar el cheque.".format(check.reject_move_id.name))
        else:
            if self.create_moves and not check.reject_move_id:
                check.create_reject_move()
            check.reject_check()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
