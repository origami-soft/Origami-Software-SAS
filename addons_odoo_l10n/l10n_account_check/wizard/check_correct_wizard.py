# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class CheckCorrectWizard(models.TransientModel):
    _name = 'check.correct.wizard'
    _description = 'Wizard de corrección de cheques'

    own_check_id = fields.Many2one('account.own.check', "Cheque propio")
    third_check_id = fields.Many2one('account.third.check', "Cheque de terceros")
    common_check = fields.Boolean()
    check_issue_date = fields.Date("Fecha de emisión", required=True)
    check_payment_date = fields.Date("Fecha de pago", required=True)
    check_name = fields.Char("Número", required=True)
    
    def get_check(self):
        return self.own_check_id or self.third_check_id
    
    @api.onchange('own_check_id', 'third_check_id')
    def onchange_check(self):
        check = self.get_check()
        self.update({
            'check_issue_date': check.issue_date,
            'check_payment_date': check.payment_date,
            'check_name': check.name,
            'common_check': check.check_type == 'common',
        })
    
    @api.onchange('check_issue_date')
    def onchange_check_issue_date(self):
        if self.common_check:
            self.check_payment_date = self.check_issue_date
    
    def correct(self):
        check = self.get_check()
        previous_number = check.name
        check.write({
            'issue_date': self.check_issue_date,
            'payment_date': self.check_payment_date,
            'name': self.check_name,
        })
        check.rename_moves(previous_number)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
