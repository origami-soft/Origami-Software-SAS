# -*- encoding: utf-8 -*-

from odoo import models, fields


class PaymentImputationWizard(models.TransientModel):
    _inherit = 'payment.imputation.wizard'

    journal_id = fields.Many2one(domain=lambda l: [('type', 'in', ('bank', 'cash')), ("company_id", "=", l.env.company.id), ('selectable_in_payments', '=', True)])

    def get_journal_domain(self):
        res = super().get_journal_domain()
        res.append(('selectable_in_payments', '=', True))
        return res
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
