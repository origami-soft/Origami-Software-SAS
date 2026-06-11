# -*- coding: utf-8 -*-

from odoo import models, fields, api, Command
from odoo.exceptions import ValidationError
from odoo.tools.misc import clean_context


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    perception_ids = fields.One2many(
        'expense.sheet.perception',
        'sheet_id',
        string='Percepciones',
        copy=True
    )

    total_perception_amount = fields.Monetary(
        string="Percepciones",
        currency_field='company_currency_id',
        compute='_compute_perception_amount',
        store=True,
    )

    @api.depends('perception_ids.amount', 'perception_ids.currency_id')
    def _compute_perception_amount(self):
        for sheet in self:
            sheet.total_perception_amount = sum(
                sheet.perception_ids.mapped('company_currency_amount')
            )

    @api.depends('total_perception_amount')
    def _compute_amount(self):
        super()._compute_amount()
        for sheet in self:
            sheet.total_amount += sheet.total_perception_amount

    def get_perception_base(self):
        """ Obtengo la base sobre la cual voy a calcular las percepciones """
        self.ensure_one()
        return round(sum(self.expense_line_ids.mapped('untaxed_amount_currency')), 2)

    def get_perception_ctx(self):
        """ Construyo el contexto de percepciones para el cálculo de impuestos """
        vals = {'base': self.get_perception_base()}
        for p in self.perception_ids:
            tax = p.perception_id.get_taxes(self.company_id)
            if not tax:
                raise ValidationError(
                    f"No hay impuesto que contenga la percepción {p.name}\n"
                    f"Por favor asociar la percepción al impuesto correspondiente en la configuración de impuestos"
                )
            elif len(tax) > 1:
                raise ValidationError(
                    f"Hay más de un impuesto que tiene configurada la percepción {p.name}\n"
                    f"Por favor revisar la configuración de los impuestos {', '.join(tax.mapped('name'))}"
                )
            vals[tax] = p.amount
        return vals

    @api.onchange('expense_line_ids')
    def onchange_set_perception_values(self):
        if self.perception_ids:
            perc_base = self.get_perception_base()
            for perception in self.perception_ids:
                perception.base = perc_base
                perception.onchange_aliquot()


    def _do_create_moves(self):
        """Sobreescribe la creación de moves para escribir las percepciones en el move
        mientras está en estado DRAFT, antes de publicarlo.

        El write() de account.move en l10n_ar_perceptions enlaza automáticamente
        los impuestos de percepción a las líneas de la factura y dispara el
        recálculo de _compute_all_tax con el perception_ctx correcto.
        """
        self = self.with_context(clean_context(self.env.context))
        skip_context = {
            'skip_invoice_sync': True,
            'skip_invoice_line_sync': True,
            'skip_account_move_synchronization': True,
        }
        own_account_sheets = self.filtered(lambda sheet: sheet.payment_mode == 'own_account')
        company_account_sheets = self - own_account_sheets

        moves = self.env['account.move'].create([
            sheet._prepare_bills_vals() for sheet in own_account_sheets
        ])
        for move in moves:
            move.message_main_attachment_id = move.attachment_ids[0] if move.attachment_ids else None

        ### Inicio de la modificación ###
        # Escribir percepciones en los moves DRAFT antes de publicar.
        # Esto dispara el write() override de l10n_ar_perceptions que vincula
        # los impuestos de percepción a las invoice_line_ids del move.
        for sheet, move in zip(own_account_sheets, moves):
            if sheet.perception_ids:
                perception_vals = []
                for p in sheet.perception_ids:
                    perception_vals.append(Command.create({
                        'perception_id': p.perception_id.id,
                        'jurisdiction': p.jurisdiction,
                        'name': p.name,
                        'base': p.base,
                        'aliquot': p.aliquot,
                        'amount': p.amount,
                    }))
                move.write({'perception_ids': perception_vals})
        ### Fin de la modificación ###

        payments = self.env['account.payment'].with_context(**skip_context).create([
            expense._prepare_payments_vals()
            for expense in company_account_sheets.expense_line_ids
        ])
        moves |= payments.move_id
        # Accion del metodo original, comentado para evitar la publicacion automatica
        # moves.action_post() 
        self.activity_update()

        return moves

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: