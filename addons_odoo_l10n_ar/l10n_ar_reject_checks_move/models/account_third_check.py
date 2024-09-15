# -*- encoding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import ValidationError


class AccountThirdCheck(models.Model):
    _inherit = 'account.third.check'

    def get_reject_move_vals(self, move_date):
        debit_line = {}
        credit_line = {}
        message = 'Rechazo de cheque de tercero: {}'.format(self.name)
        # Entregado: cuenta a cobrar del partner origen VS cuenta a pagar partner destino.
        # Ambas líneas deben tener su partner correspondiente.
        if self.state == 'handed':
            # Debe
            if not self.partner_id:
                raise ValidationError("El cheque no tiene partner origen.")
            if not self.destination_partner_id:
                raise ValidationError("El cheque no tiene partner destino.")
            debit_line = self._get_reject_move_line(
                self.partner_id.property_account_receivable_id,
                debit=self.amount,
                partner_id=self.partner_id.id,
                reference=message,
            )
            # Haber
            credit_line = self._get_reject_move_line(
                self.destination_partner_id.property_account_payable_id,
                credit=self.amount,
                partner_id=self.destination_partner_id.id,
                reference=message
            )

        # En cartera:  cuenta a cobrar del partner origen VS cuenta contable del diario.
        # La linea con la cuenta a cobrar tiene que tener partner.
        elif self.state == 'wallet':
            # Debe
            if not self.partner_id:
                raise ValidationError("El cheque no tiene partner origen.")
            debit_line = self._get_reject_move_line(
                self.partner_id.with_company(self.company_id).property_account_receivable_id,
                debit=self.amount,
                partner_id=self.partner_id.id
            )
            # Haber
            credit_line = self._get_reject_move_line(
                self.journal_id._get_journal_inbound_outstanding_payment_accounts()[0],
                credit=self.amount
            )
        # Depositado:  cuenta a cobrar del partner origen VS cuenta del depósito.
        # La linea con la cuenta a cobrar tiene que tener partner.
        elif self.state == 'deposited':
            # Debe
            if not self.partner_id:
                raise ValidationError("El cheque no tiene partner origen.")
            debit_line = self._get_reject_move_line(
                self.partner_id.with_company(self.company_id).property_account_receivable_id,
                debit=self.amount,
                partner_id=self.partner_id.id
            )
            # Haber
            credit_line = self._get_reject_move_line(
                self.deposit_bank_id._get_journal_inbound_outstanding_payment_accounts()[0],
                credit=self.amount
            )

        vals = {
            'date': move_date,
            'ref': 'Rechazo de cheque: {}'.format(self.name),
            'journal_id': self.journal_id.id,
            'line_ids': [(0, 0, debit_line), (0, 0, credit_line)]
        }
        return vals

    def _get_reject_move_line(self, account, debit=0.0, credit=0.0, partner_id=False, reference=''):
        """
        Crea una move line de la venta de cheques y las asocia al move
        :param account: Cuenta contable de la linea del asiento
        :param debit: Importe en el haber de la move line
        :param credit: Importe en el haber de la move line
        :param partner_id: Id del partner de la linea del asiento (opcional)
        :param reference: Descripcion de la linea contable
        :return: account.move.line creada
        """
        move_line_vals = {
            'debit': debit,
            'credit': credit,
            'name': reference,
            'account_id': account.id,
            'partner_id': partner_id,
        }
        return move_line_vals
    
    def revert_reject(self):
        res = super().revert_reject()
        # Cancelamos y borramos el asiento
        self.reject_move_id.button_draft()
        self.reject_move_id.button_cancel()
        self.reject_move_id.with_context(force_delete=True).unlink()
        self.reject_date = False
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
