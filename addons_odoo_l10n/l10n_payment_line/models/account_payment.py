# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from ..exceptions import exceptions


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    journal_id = fields.Many2one(comodel_name='account.journal', compute='_compute_journal_id', store=True, readonly=False, precompute=True,
        check_company=True,
        domain="[('id', 'in', available_journal_ids)]")
    show_payment_lines = fields.Boolean(compute='get_show_payment_lines')
    payment_usage = fields.Selection(related='journal_id.payment_usage')
    move_ids = fields.One2many('account.move', 'payment_id')
    available_journal_ids = fields.Many2many('account.journal', compute='get_available_journals')

    @api.depends('available_journal_ids')
    def _compute_journal_id(self):
        for wizard in self:
            if wizard.can_edit_wizard:
                batch = wizard._get_batches()[0]
                wizard.journal_id = wizard._get_batch_journal(batch)
            else:
                wizard.journal_id = self.env['account.journal'].search([
                    *self.env['account.journal']._check_company_domain(wizard.company_id),
                    ('type', 'in', ('bank', 'cash')),
                    ('id', 'in', self.available_journal_ids.ids)
                ], limit=1)

    @api.depends_context('default_is_internal_transfer')
    @api.depends('partner_id', 'journal_id', 'destination_journal_id')
    def _compute_is_internal_transfer(self):
        res = super(AccountPayment, self)._compute_is_internal_transfer()
        if self.env.context.get('default_is_internal_transfer'):
            self.with_context(skip_account_move_synchronization=True).write({
                'is_internal_transfer': True
            })
        return res

    def _get_available_journal_domain(self):
        domain = [('type', 'in', ('bank', 'cash')), ('company_id', '=', self.company_id.id)]
        if not self.is_internal_transfer:
            domain.append(('selectable_in_payments', '=', True))
        return domain

    @api.depends('is_internal_transfer', 'company_id')
    def get_available_journals(self):
        for r in self:
            r.available_journal_ids = r.env['account.journal'].search(r._get_available_journal_domain())

    @api.depends('payment_method_code', 'journal_id.payment_usage')
    def _compute_show_require_partner_bank(self):
        res = super(AccountPayment, self)._compute_show_require_partner_bank()
        for payment in self:
            payment.show_partner_bank_account = payment.show_partner_bank_account and payment.journal_id.payment_usage != 'document_book'
        return res

    def unlink(self):
        """
        Heredo el método unlink() ya que, al eliminar un pago, si no se define explícitamente eliminar las líneas
        también Odoo intentará poner NULL en todos los campos de las líneas, generando errores por constraint not null
        """
        payment_line_fields = self.get_payment_line_fields()
        for line_field in payment_line_fields:
            self.mapped(line_field).unlink()
        return super(AccountPayment, self).unlink()

    @api.onchange('is_internal_transfer', 'journal_id')
    def onchange_clear_lines(self):
        if not self.show_payment_lines:
            for field in self.get_payment_line_fields():
                setattr(self, field, False)

    def get_payment_line_fields(self):
        return []

    def _get_show_payment_lines(self):
        return self.payment_usage == 'document_book' and not self.is_internal_transfer

    @api.depends('payment_usage', 'is_internal_transfer')
    def get_show_payment_lines(self):
        for r in self:
            r.show_payment_lines = r._get_show_payment_lines()
    
    def recalculate_payment_amount(self):
        self.amount = self.get_payment_line_total()
    
    def get_journal_debit_account(self):
        accounts = self.journal_id._get_journal_inbound_outstanding_payment_accounts()
        return accounts[0].id if accounts else False

    def get_journal_credit_account(self):
        accounts = self.journal_id._get_journal_outbound_outstanding_payment_accounts()
        return accounts[0].id if accounts else False
    
    def get_second_payment_line_move_line_name(self):
        return self.name

    def get_payment_line_total(self):
        total = 0
        for recordset in self._get_payment_line_recordsets():
            total += sum(getattr(r, r.get_amount_field(self)) for r in recordset)
        return round(total, 2)

    def validate_equal_amounts(self):
        return all(r.payment_usage != 'document_book' or r.get_payment_line_total() == round(r.amount, 2) for r in self)

    @api.onchange('journal_id', 'currency_id', 'date', 'company_id')
    def onchange_update_rates(self):
        """ Si cambio la compañía del pago o la fecha, actualizo las cotizaciones de las líneas """
        for recordset in self._get_payment_line_recordsets():
            for r in recordset:
                r.onchange_update_rate()
                r.onchange_amount()

    def _get_payment_line_recordsets(self):
        return [getattr(self, field) for field in self.get_payment_line_fields()]

    def create_line_moves(self):
        """
        Heredo la función que define los datos con los cuales se generarán los asientos para crear asientos adicionales
        en caso de que se definan métodos de pago (uno por cada método)
        """
        vals = []
        if not self.is_internal_transfer:
            for recordset in self._get_payment_line_recordsets():
                vals.extend([r.get_move_vals(self) for r in recordset])
        return self.env['account.move'].create(vals)
    
    def _check_journal_and_payment_on_same_currency(self):
        """ 
            Descripción de casos contemplados
            Moneda del diario | Moneda del pago | Error |
            -                 | Compañia        | No    |
            -                 | Extranjera 1    | Si    |
            Extranjera 1      | Compañia        | Si    |
            Extranjera 1      | Extranjera 2    | Si    |
        """
        for rec in self:
            if (rec.journal_id.currency_id or rec.currency_id != rec.company_id.currency_id) \
                and rec.journal_id.currency_id != rec.currency_id:
                exceptions.journal_and_payment_on_different_currency(rec.journal_id, rec.currency_id)

    def action_post(self):
        """
        Paso por contexto que no se actualicen las cotizaciones de las líneas de métodos para evitar que la validación
        del pago pise las cotizaciones introducidas
        """
        self._check_journal_and_payment_on_same_currency()
        if any(not r.is_internal_transfer and not r.validate_equal_amounts() for r in self):
            exceptions.not_equal_amounts()
        res = super(AccountPayment, self.with_context(do_not_update_rates=True)).action_post()
        for r in self.filtered(lambda l: not l.is_internal_transfer and l.payment_usage == 'document_book'):

            # Creo y valido los apuntes correspondientes a los métodos de pago
            line_moves = r.create_line_moves()
            line_moves._post(soft=False)

            # Concilio entre sí todos los apuntes que tengan la cuenta del diario del pago (serán el apunte del pago y
            # los de las grillas)
            lines = r.move_ids.mapped('line_ids')
            inbound_payment = r.payment_type == 'inbound'
            account = r.get_journal_debit_account() if inbound_payment else r.get_journal_credit_account()
            lines.filtered(lambda l: l.account_id.id == account and not l.reconciled).reconcile()
        return res
    
    def action_draft(self):
        line_moves = self.mapped('move_ids') - self.mapped('move_id')
        line_moves.button_draft()
        line_moves.with_context(force_delete=True).unlink()
        return super().action_draft()
    
    def button_open_journal_entry(self):
        res = super().button_open_journal_entry()
        ids = self.move_ids.ids
        if len(ids) > 1:
            res['view_mode'] = 'tree,form'
            res.pop('res_id')
            res['domain'] = [('id', 'in', ids)]
        return res

    def _synchronize_to_moves(self, changed_fields):
        # Defino así el contexto porque con self.with_context no llega hasta _seek_for_lines
        ctx = self.env.context.copy()
        ctx['force_liquidity'] = True
        self.env.context = ctx
        super()._synchronize_to_moves(changed_fields)
        if 'ref' in changed_fields:
            for r in self:
                payment_line_moves = r.move_ids - r.move_id
                payment_line_moves.write({'ref': r.ref})
    
    def _synchronize_from_moves(self, changed_fields):
        # Defino así el contexto porque con self.with_context no llega hasta _seek_for_lines
        ctx = self.env.context.copy()
        ctx['force_liquidity'] = True
        self.env.context = ctx
        super()._synchronize_from_moves(changed_fields)
    
    def _is_old_payment(self):
        """
        Método auxiliar para ver si el pago corresponde al formato de localizaciones anteriores
        (debe tener un solo asiento y alguna de las grillas de medios de pago cargada)
        """
        self.ensure_one()
        return len(self.move_ids) == 1 and any(rset for rset in self._get_payment_line_recordsets())
    
    def _seek_for_lines(self):
        """
        Como los asientos de pago de las versiones viejas no tienen un formato compatible con la versión 15, altero los
        valores a devolver para satisfacer el criterio de _synchronize_to_moves
        res[0] es liquidity_lines, el apunte que comparte cuenta con el diario de pago. Como en los asientos viejos no
        hay ninguno que cumpla con ese criterio, armo un pseudo-apunte con new que contenga los datos que necesito para
        el _synchronize_to_moves, basándome en el apunte a cobrar/pagar pero con un importe opuesto
        res[1] es counterpart_lines, el apunte que posee una cuenta a cobrar/pagar
        res[2] es writeoff_lines, todos los demás apuntes. En los asientos viejos, son todos los de los medios de pago,
        pero _synchronize_to_moves exige que todos los writeoff_lines tengan la misma cuenta (lo cual si hay más de un
        medio de pago es imposible), así que lo reemplazo por un recordset vacío (no se usan los datos de los apuntes,
        solamente se realiza la validación)
        """
        res = super()._seek_for_lines()
        # Me fijo que el asiento esté compuesto por un apunte con cuenta a cobrar/pagar y sea del formato de
        # localizaciones anteriores
        if self.env.context.get('force_liquidity') and not res[0] and len(res[1]) == 1 and self._is_old_payment():
            liquidity = self.env['account.move.line'].new({
                'amount_currency': -res[1].amount_currency,
                'currency_id': res[1].currency_id,
                'partner_id': res[1].partner_id
            })
            return (liquidity, res[1], self.env['account.move.line'])
        return res
    
    @api.depends('amount_total_signed', 'payment_type')
    def _compute_amount_company_currency_signed(self):
        """
        Piso el método que calcula el total a mostrar en la lista para que, en los pagos de versiones anteriores, lo
        calcule en base a la línea a cobrar/pagar (ya que normalmente usa la línea cuya cuenta coincide con la de
        recibos/pagos pendientes del diario)
        """
        old_payments = self.filtered(lambda l: l._is_old_payment())
        for payment in old_payments:
            lines = payment._seek_for_lines()[1]
            payment.amount_company_currency_signed = -sum(lines.mapped('balance'))
        super(AccountPayment, self - old_payments)._compute_amount_company_currency_signed()
   
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
