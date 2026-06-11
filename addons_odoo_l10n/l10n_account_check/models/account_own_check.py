# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from ..exceptions import exceptions


class AccountOwnCheck(models.Model):
    _inherit = 'account.abstract.check'
    _name = 'account.own.check'
    _description = 'Cheque propio'

    destination_payment_id = fields.Many2one(
        'account.payment',
        "Pago origen",
        help="Pago donde se utilizó el cheque",
        tracking=True
    )
    destination_partner_id = fields.Many2one(
        related='destination_payment_id.partner_id',
        store=True
    )
    journal_id = fields.Many2one(
        domain="[('company_id', '=', company_id), ('payment_usage', '=', 'own_check')]"
    )
    bank_journal_id = fields.Many2one(
        'account.journal',
        string="Banco",
        required=True,
        domain="[('company_id', '=', company_id), ('type', '=', 'bank'), ('bank_id', '!=', False)]",
        compute='_compute_default_bank_journal_id',
        store=True,
        readonly=False
    )

    @api.constrains('name', 'bank_id')     
    def _check_unique_own_check(self):                                                                              
        for rec in self:                   
            if rec.name and rec.bank_id:
                duplicate = self.search([                                                                           
                    ('name', '=', rec.name),
                    ('bank_id', '=', rec.bank_id.id),                                                               
                    ('id', '!=', rec.id),                                                                           
                ], limit=1)
                if duplicate:                                                                                       
                    raise exceptions.ValidationError(
                        "No puede registrar 2 cheques propios con el mismo número y banco."
                    )

    @api.depends('company_id', 'payment_id')
    def _compute_default_bank_journal_id(self):
        for rec in self:
            if not rec.bank_journal_id and not rec._origin.bank_journal_id:
                rec.bank_journal_id = rec.company_id.own_check_bank_id
            else:
                rec.bank_journal_id = rec.bank_journal_id

    @api.onchange('bank_journal_id')
    def onchange_bank_journal_set_bank(self):
        self.bank_id = self.bank_journal_id.bank_id

    def get_states(self):
        res = super(AccountOwnCheck, self).get_states()
        res.insert(2, ('canceled', 'Anulado'))
        return res

    def _check_post_payment_state(self):
        return self.state == 'draft'

    def post_payment(self, vals):
        """ Lo que deberia pasar con el cheque cuando se valida el pago """
        if any(not r._check_post_payment_state() for r in self):
            exceptions.post_payment_non_draft_check()
        self.update(vals or {})
        self.next_state('draft_handed')

    def cancel_payment(self):
        """ Lo que deberia pasar con el cheque cuando se cancela una orden de pago """
        if any(not r._check_state_for_cancel_payment() for r in self):
            exceptions.cancel_payment_non_handed_check()
        self.update({'destination_payment_id': None})
        self.cancel_state('handed')

    def get_cancel_states(self):
        return {
            'handed': 'draft',
        }

    def get_next_states(self):
        return {
            'draft_handed': 'handed',
        }

    def get_name_for_move_line(self):
        return 'CHEQUE PROPIO N° {}'.format(self.name)
    
    def open_correct_wizard(self):
        res = super().open_correct_wizard()
        res['context'] = {'default_own_check_id': self.id}
        return res

    def modify_maturity_date(self, payment):
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
