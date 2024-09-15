# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountThirdCheck(models.Model):
    _inherit = 'account.third.check'

    @api.depends('sold_check_ids')
    def get_sold_check_id(self):
        for check in self:
            check.sold_check_id = check.sold_check_ids[0].id\
                if check.sold_check_ids else None

    sold_check_ids = fields.Many2many(
        'account.sold.check',
        'third_check_sold_check_rel',
        'third_check_id',
        'sold_check_id',
        string='Documentos de venta de cheques'
    )
    sold_check_id = fields.Many2one(
        'account.sold.check',
        'Documento de venta',
        compute='get_sold_check_id',
        store=True
    )
    sold_bank_id = fields.Many2one(
        'account.journal',
        'Cuenta bancaria de venta',
        related='sold_check_id.bank_account_id',
        readonly=True
    )
    sold_partner_id = fields.Many2one(
        'res.partner',
        'Vendido a',
        related='sold_check_id.partner_id',
        readonly=True
    )
    sold_date = fields.Date(
        'Fecha de venta',
        related='sold_check_id.date',
        store=True,
        readonly=True
    )

    @api.constrains('sold_check_ids')
    def sold_check_contraints(self):
        if any(check.state != 'wallet' for check in self):
            raise ValidationError('Solo se puede modificar el documento de venta de un cheque en cartera.')
        for check in self:
            if len(check.sold_check_ids) > 1:
                raise ValidationError("El cheque {} ya se encuentra en un documento de venta.".format(check.name))

    def post_sold_check(self):
        if any(check.state != 'wallet' for check in self):
            raise ValidationError("Todos los cheques a vender deben estar en cartera.")
        if len(self.mapped('currency_id')) > 1:
            raise ValidationError("No se pueden depositar cheques de distintas monedas en la misma venta.")
        self.next_state('wallet_sold')

    def cancel_sold_check(self):
        if any(check.state not in ('sold', 'wallet') for check in self):
            raise ValidationError("Para cancelar el documento de venta de cheques"
                                  " los cheques deben estar vendidos o en cartera.")
        self.cancel_state('sold')

    def revert_reject(self):
        if any(check.state != 'rejected' for check in self):
            raise ValidationError("No se puede revertir el rechazo de un cheque que no está rechazado.")

        for check in self:
            # Si antes de rechazarse estaba vendido
            if check.sold_check_id:
                check.cancel_state('rejected_sold')
            else:
                super(AccountThirdCheck, check).revert_reject()

    def get_next_states(self):
        res = super(AccountThirdCheck, self).get_next_states()
        res.update({'wallet_sold': 'sold', 'sold': 'rejected'})
        return res

    def get_cancel_states(self):
        res = super(AccountThirdCheck, self).get_cancel_states()
        res.update({'sold': 'wallet', 'rejected_sold': 'sold'})
        return res

    def get_states(self):
        res = super(AccountThirdCheck, self).get_states()
        res.insert(5, ('sold', 'Vendido'))
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
