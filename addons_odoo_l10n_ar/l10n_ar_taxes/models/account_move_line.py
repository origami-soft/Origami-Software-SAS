# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    @api.constrains('tax_ids')
    def check_more_than_one_vat_in_line(self):
        """ Se asegura que no haya mas de un impuesto tipo IVA en las lineas de factura """
        for move_line in self:
            if len(move_line.tax_ids.filtered(lambda r: r.is_vat)) > 1:
                raise ValidationError("No puede haber más de un impuesto de tipo IVA en una línea")

    @api.model_create_multi
    def create(self, vals_list):
        """ En caso de estar dando de alta una línea de IVA en moneda extranjera, hago que el importe coincida con el
        importe en moneda extranjera * la cotización, ya que Odoo hace la conversión base tomando todos los decimales
        del IVA pero redondea a la hora de guardar el importe en moneda, lo cual puede generar discrepancias
        """
        for vals in vals_list:
            tax_rep_line_id = vals.get('tax_repartition_line_id')
            currency_id = vals.get('currency_id')
            company_curr = self.env['res.company'].browse(vals.get('company_id')).currency_id
            if tax_rep_line_id and currency_id and currency_id != company_curr.id:
                tax = self.env['account.tax.repartition.line'].browse(tax_rep_line_id).tax_id
                if tax.is_vat:
                    move = self.env['account.move'].browse(vals.get('move_id'))
                    rate = move.currency_rate or move.current_currency_rate
                    vals['balance'] = vals['amount_currency'] * (rate or 1)
        return super().create(vals_list)

    def write(self, vals):
        """ En caso de estar modificando una línea de IVA en moneda extranjera, hago que el importe coincida con el
        importe en moneda extranjera * la cotización, ya que Odoo hace la conversión base tomando todos los decimales
        del IVA pero redondea a la hora de guardar el importe en moneda, lo cual puede generar discrepancias
        """
        if len(self) == 1:
            tax_rep_line_id = vals.get('tax_repartition_line_id')
            currency_id = vals.get('currency_id')
            company_curr = self.company_currency_id
            if tax_rep_line_id and currency_id and currency_id != company_curr.id:
                tax = self.env['account.tax.repartition.line'].browse(tax_rep_line_id).tax_id
                if tax.is_vat:
                    vals['balance'] = vals['amount_currency'] / (self.currency_rate or 1)
        return super().write(vals)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
