# -*- encoding: utf-8 -*-

from odoo import models, api

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.onchange('journal_id', 'currency_id', 'company_id')
    def onchange_update_rates(self):
        """ Si cambio la compañía del pago o la fecha, actualizo las cotizaciones de las líneas """
        res = super(AccountPayment, self).onchange_update_rates()
        for r in self.account_third_check_sent_ids:
            r.onchange_natural_sent_rate()
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
