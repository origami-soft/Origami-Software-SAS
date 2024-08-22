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

from odoo import models, fields, api


class AccountAbstractCheck(models.AbstractModel):
    _inherit = 'account.abstract.check'

    check_location_id = fields.Many2one(
        comodel_name='account.check.location',
        string='Ubicación'
    )

    def _check_name(self):
        """ Piso la funcion para que no cheque que es numerico """
        if self.check_location_id.prefix:
            return True
        else:
            return super(AccountAbstractCheck, self)._check_name()

    @api.model
    def create(self, vals):
        """ Heredo el create para que se agregue el prefijo de la ubicación del cheque a su número """
        res = super(AccountAbstractCheck, self).create(vals)
        if res.check_location_id.prefix:
            res.name = "({}) {}".format(res.check_location_id.prefix, res.name)
        return res

    def write(self, vals):
        """ Heredo el write para que, al guardar cambios, el número del cheque quede con el prefijo correspondiente """
        prev_prefixes = {}
        # En caso de estar cambiando la ubicación, me guardo el prefijo que cada cheque tenía antes de los cambios
        if not self.env.context.get('check_location_flag') and 'check_location_id' in vals:
            for r in self.filtered(lambda l: l.check_location_id.prefix):
                prev_prefixes[r] = r.check_location_id.prefix
        res = super(AccountAbstractCheck, self).write(vals)
        if not self.env.context.get('check_location_flag') and ('check_location_id' in vals or 'name' in vals):
            for r in self:
                new_name = r.name
                # Tomo el prefijo anterior (el de la ubicación anterior en caso de estar cambiándola, el de la actual
                # en el caso contrario) y lo saco del número del cheque
                prev_prefix = prev_prefixes.get(r) if 'check_location_id' in vals else r.check_location_id.prefix
                if prev_prefix:
                    new_name = new_name.replace('(' + prev_prefix + ') ', '')
                # Agrego el nuevo prefijo
                if r.check_location_id.prefix:
                    new_name = "({}) {}".format(r.check_location_id.prefix, new_name)
                r.with_context(check_location_flag=True).write({'name': new_name})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
