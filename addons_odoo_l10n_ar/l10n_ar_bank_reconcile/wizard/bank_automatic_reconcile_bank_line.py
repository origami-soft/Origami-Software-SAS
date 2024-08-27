# -*- encoding: utf-8 -*-

from odoo import models, fields


class BankAutomaticReconcileBankLine(models.TransientModel):

    _name = 'bank.automatic.reconcile.bank.line'

    name = fields.Char('Descripción')
    debit = fields.Float('Debe')
    credit = fields.Float('Haber')
    date = fields.Char('Fecha')
    bank_automatic_reconcile_id = fields.Many2one('bank.automatic.reconcile.wizard', 'Conciliacion automatica')


class BankAutomaticReconcileFoundLine(models.TransientModel):

    _name = 'bank.automatic.reconcile.found.line'
    _order = 'move_line_date asc'

    move_line_id = fields.Many2one('account.move.line', required=True)
    move_line_date = fields.Date(related='move_line_id.date', string='Fecha', readonly=1)
    move_line_name = fields.Char(related='move_line_id.name', string='Etiqueta', readonly=1)
    move_line_ref = fields.Char(related='move_line_id.ref', string='Referencia', readonly=1)
    move_line_partner_id = fields.Many2one(related='move_line_id.partner_id', readonly=1)
    move_line_debit = fields.Monetary(related='move_line_id.debit', currency_field='company_currency_id', string='Debito', readonly=1)
    move_line_credit = fields.Monetary(related='move_line_id.credit', currency_field='company_currency_id', string='Credito', readonly=1)
    bank_description = fields.Char('Descripción Banco', readonly=1)
    company_currency_id = fields.Many2one(related='move_line_id.company_currency_id', readonly=1)
    bank_automatic_reconcile_id = fields.Many2one('bank.automatic.reconcile.wizard', 'Conciliacion automatica')


class BankAutomaticReconcileNotFoundLine(models.TransientModel):

    _name = 'bank.automatic.reconcile.not.found.line'
    _order = 'move_line_date asc'

    move_line_id = fields.Many2one('account.move.line', required=True)
    move_line_date = fields.Date(related='move_line_id.date', string='Fecha', readonly=1)
    move_line_name = fields.Char(related='move_line_id.name', string='Etiqueta', readonly=1)
    move_line_ref = fields.Char(related='move_line_id.ref', string='Referencia', readonly=1)
    move_line_partner_id = fields.Many2one(related='move_line_id.partner_id', readonly=1)
    move_line_debit = fields.Monetary(related='move_line_id.debit', currency_field='company_currency_id', string='Debito', readonly=1)
    move_line_credit = fields.Monetary(related='move_line_id.credit', currency_field='company_currency_id', string='Credito', readonly=1)
    company_currency_id = fields.Many2one(related='move_line_id.company_currency_id', readonly=1)
    bank_automatic_reconcile_id = fields.Many2one('bank.automatic.reconcile.wizard', 'Conciliacion automatica')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
