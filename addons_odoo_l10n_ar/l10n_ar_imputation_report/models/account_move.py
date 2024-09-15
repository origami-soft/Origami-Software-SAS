# -*- encoding: utf-8 -*-

from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def get_report_imputations(self):
        imputations_lines = []
        lines_filtered_by_type = self.line_ids.filtered(lambda x: x.account_id.account_type in ['asset_receivable', 'liability_payable'])
        for line in lines_filtered_by_type.matched_credit_ids:
            total = line.credit_move_id.move_id.amount_total
            if self.currency_id != line.credit_move_id.currency_id:
                rate = self.env['res.currency']._get_conversion_rate(line.credit_move_id.currency_id, self.currency_id, self.company_id, line.credit_move_id.date)
                total = total * rate
            if line.debit_amount_currency != 0:
                matched_credit = {
                    'document': line.credit_move_id.move_id.full_voucher_name,
                    'date': line.credit_move_id.date,
                    'total': total,
                    'imputation': line.debit_amount_currency
                }
                imputations_lines.append(matched_credit)
        for line in lines_filtered_by_type.matched_debit_ids:
            total = line.debit_move_id.move_id.amount_total
            if self.currency_id != line.debit_move_id.currency_id:
                rate = self.env['res.currency']._get_conversion_rate(line.debit_move_id.currency_id, self.currency_id, self.company_id, line.debit_move_id.date)
                total = total * rate
            if line.debit_amount_currency != 0:
                matched_debit = {
                    'document': line.debit_move_id.move_id.full_voucher_name,
                    'date': line.debit_move_id.date,
                    'total': total,
                    'imputation': line.debit_amount_currency
                }
                imputations_lines.append(matched_debit)
        return sorted(imputations_lines, key=lambda k : k['date'])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
