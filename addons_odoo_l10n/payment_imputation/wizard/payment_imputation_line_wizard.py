# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

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
