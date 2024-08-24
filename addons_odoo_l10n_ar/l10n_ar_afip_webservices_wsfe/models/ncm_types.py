
# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from odoo.osv import expression


class NCMTypes(models.Model):
    _name = 'ncm.types'
    _description = 'Tipos de nomecladores comunes del Mercosur'

    name = fields.Char('Nombre', required=True)
    code = fields.Char('Código', required=True)

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        domain = domain or []
        if name:
            name_domain = ['|', ('name', operator, name), ('code', operator, name)]
            domain = expression.AND([name_domain, domain])
        return self._search(domain, limit=limit, order=order)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
