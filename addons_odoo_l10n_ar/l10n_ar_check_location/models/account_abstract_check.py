# -*- encoding: utf-8 -*-

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
        """Redefino el create generar correctamente el nombre segun la ubicacion"""
        res = super(AccountAbstractCheck, self).create(vals)
        if res.check_location_id:
            check_location = self.env['account.check.location'].browse(vals.get('check_location_id'))
            if check_location.prefix:
                res.name = "({}) {}".format(check_location.prefix, res.name.lstrip("({}) ".format(res.check_location_id.prefix)))
        return res

    def write(self, vals):
        """Redefino el write generar correctamente el nombre segun la ubicacion"""
        if 'check_location_id' in vals:
            for check in self:
                # Saco el prefijo del anterior ubicacion para que solo quede el numero del cheque
                if check.check_location_id.prefix:
                    check_name = check.name.lstrip("({}) ".format(check.check_location_id.prefix))
                    check.update({'name': check_name})
                # Saco el prefijo del anterior ubicacion para que solo quede el numero del cheque
                check_location = self.env['account.check.location'].browse(vals.get('check_location_id'))
                if check_location.prefix:
                    check_name = "({}) {}".format(check_location.prefix, check.name)
                    self.env.cr.execute("""update {} set name = '{}' where id = {}""".format(check._table, check_name, check.id))
        return super(AccountAbstractCheck, self).write(vals)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
