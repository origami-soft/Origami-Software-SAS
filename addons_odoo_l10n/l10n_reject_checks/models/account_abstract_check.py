# -*- encoding: utf-8 -*-

from odoo import models


class AccountAbstractCheck(models.AbstractModel):
    _inherit = 'account.abstract.check'

    def get_states(self):
        res = super(AccountAbstractCheck, self).get_states()
        res.append(('rejected', 'Rechazado'))
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
