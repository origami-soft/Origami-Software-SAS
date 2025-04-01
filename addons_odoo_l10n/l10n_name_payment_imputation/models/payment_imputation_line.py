# -*- encoding: utf-8 -*-

from odoo import models


class AbstractPaymentImputationLine(models.AbstractModel):
    _inherit = 'abstract.payment.imputation.line'

    def _compute_name(self):
        for line in self:
            line.name = line.move_line_id.full_voucher_name or line.move_line_id.name

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
