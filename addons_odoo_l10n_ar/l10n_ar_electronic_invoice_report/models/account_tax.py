# -*- encoding: utf-8 -*-

from odoo import models, _


class AccountTax(models.Model):

    _inherit = 'account.tax'

    def get_tax_description(self):
        # EJ: IVA 21.0%
        tax_group_internal = self.get_internal_tax_group(self.company_id)
        if self.tax_group_id == self.env.ref('l10n_ar.tax_group_vat'):
            res = _('VAT ') + str(self.amount) + '%'
        elif self.tax_group_id == tax_group_internal:
            res = _('INTERNAL TAX ') + self.description or ''
        else:
            res = self.description
        return res
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
