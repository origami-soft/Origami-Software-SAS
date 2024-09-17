from odoo import fields, models, api


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    full_voucher_name = fields.Char(
        "Número completo",
        compute='compute_full_voucher_name',
        store=True,
    )

    def compute_full_voucher_name(self):
        for r in self:
            r.full_voucher_name = r.move_id.full_voucher_name if r.move_id.full_voucher_name else r.move_id.name
