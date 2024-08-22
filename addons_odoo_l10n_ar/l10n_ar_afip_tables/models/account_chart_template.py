# -*- encoding: utf-8 -*-

from odoo import models


class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'

    def try_loading(self, template_code, company, install_demo=True):
        res = super(AccountChartTemplate, self).try_loading(template_code, company, install_demo)
        if template_code == 'ar':
            company.create_tax_codes_models()
        else:
            company.delete_tax_codes_models()
        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
