# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CreditCardInstallment(models.Model):
    _inherit = 'credit.card.installment'

    reconciled = fields.Boolean('Conciliado', readonly=True)
    concile_ids = fields.Many2many(
        'credit.card.installment.concile',
        'credit_card_installment_concile_rel',
        'installment_id',
        'concile_id',
        string='conciliaciones'
    )

    @api.constrains('concile_ids')
    def constraint_multiple_conciliations(self):
        for installment in self:
            if len(installment.concile_ids) > 1:
                raise ValidationError("Una cuota no puede pertenecer a múltiples conciliaciones.")

    def reconcile(self):
        self.write({'reconciled': True})

    def cancel_reconcile(self):
        self.write({'reconciled': False})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
