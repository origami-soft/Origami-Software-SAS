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

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_arba_cot_enabled = fields.Boolean(
        "Usar COT de ARBA",
        help='Permite generar el COT de arba una vez que se han asignado '
        'números de remitos en las entregas',
        implied_group='l10n_ar_cot_arba.arba_cot_enabled',
    )
    cot_arba_key = fields.Char(
        related='company_id.cot_arba_key',
        readonly=False,
    )
    cot_path_type = fields.Selection(
        related='company_id.cot_path_type',
        readonly=False,
    )

    cot_partner_id = fields.Many2one(
        related='company_id.cot_partner_id',
        readonly=False,
    )

    cot_prod_no_term_dev = fields.Selection(
        related='company_id.cot_prod_no_term_dev',
        readonly=False,
    )


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
