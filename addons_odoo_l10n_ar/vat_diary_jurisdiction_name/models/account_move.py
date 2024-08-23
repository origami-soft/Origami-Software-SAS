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

from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def get_vat_diary_dict(self):
        vals = super().get_vat_diary_dict()
        jurisdiction = self.jurisdiction_id or self.partner_id.state_id
        vals.update({
            'fiscal_position': self.fiscal_position_id.reports_name or vals['fiscal_position'],
            'jurisdiction': jurisdiction.reports_name or jurisdiction.name or '',
        })
        return vals

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
