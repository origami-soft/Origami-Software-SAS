# -*- encoding: utf-8 -*-

from odoo import models, fields


class AccountTaxRepartitionLine(models.Model):
    _inherit = 'account.tax.repartition.line'

    amount_type = fields.Char(compute='get_amount_type')

    def get_amount_type(self):
        for r in self:
            r.amount_type = r.tax_id.amount_type

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
