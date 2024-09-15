# -*- encoding: utf-8 -*-

from odoo import models, fields


class PaymentImputationLineWizardAbstract(models.AbstractModel):

    _name = 'payment.imputation.line.wizard.abstract'
    _inherit = 'abstract.payment.imputation.line'
    _description = 'Linea de imputacion para wizard abstracta'

    payment_id = fields.Many2one('payment.imputation.wizard')


class PaymentImputationCreditLineWizard(models.TransientModel):

    _name = 'payment.imputation.credit.line.wizard'
    _inherit = 'payment.imputation.line.wizard.abstract'
    _description = 'Linea de imputacion de credito para wizard abstracta'


class PaymentImputationDebitLineWizard(models.TransientModel):

    _name = 'payment.imputation.debit.line.wizard'
    _inherit = 'payment.imputation.line.wizard.abstract'
    _description = 'Linea de imputacion de debito para wizard abstracta'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
