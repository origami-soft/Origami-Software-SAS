# -*- encoding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import ValidationError


class AfipImportDocumentsLineWizard(models.TransientModel):

    _name = 'afip.import.documents.line.wizard'

    date = fields.Date(
        string='Fecha'
    )
    voucher_type = fields.Char(
        string='Tipo'
    )
    point_of_sale = fields.Char(
        string='Punto de venta'
    )
    voucher_name = fields.Char(
        string='Numero'
    )
    cae = fields.Char(
        sring='CAE'
    )
    document_type = fields.Char(
        string='Tipo de documento'
    )
    document_number = fields.Char(
        string='Numero de documento'
    )
    name = fields.Char(
        string='Denominación'
    )
    currency_value = fields.Float(
        string='Tipo de cambio'
    )
    currency = fields.Char(
        string='Moneda'
    )
    amount_untaxed = fields.Float(
        string='Importe neto gravado'
    )
    amount_not_taxed = fields.Float(
        string='Importe no gravado'
    )
    amount_exempt = fields.Float(
        string='Importe exento'
    )
    amount_other_tributes = fields.Float(
        string='Importe otros tributos'
    )
    amount_vat = fields.Float(
        string='Importe IVA'
    )
    amount_total = fields.Float(
        string='Importe Total'
    )
    wizard_id = fields.Many2one(
        comodel_name='afip.import.documents.wizard',
        string='Wizard',
    )

    def get_invoice_lines(self):
        self.ensure_one()
        lines = []
        base_vals = {
            'quantity': 1,
        }
        # En caso de que AFIP informe un neto gravado, agrego una línea para el mismo
        if self.amount_untaxed:
            line_vals = {'name': "Neto gravado", 'price_unit': self.amount_untaxed}
            # Obtengo el porcentaje de IVA a partir del cociente entre el importe de IVA y el neto gravado
            tax_percentage = round(100 * self.amount_vat / self.amount_untaxed if self.amount_untaxed else 0, 2)
            # Busco un impuesto IVA con el porcentaje obtenido
            tax = self._get_vat_tax(tax_percentage)
            # En caso de encontrar un impuesto, le asigno el impuesto en cuestión a la línea
            if tax:
                line_vals['tax_ids'] = [(6, 0, tax.ids)]
                # En caso de que impuesto esté configurado para estar incluido en el precio, sumo el IVA al precio unitario
                # para mantener el subtotal y total intactos
                if tax.price_include:
                    line_vals['price_unit'] += self.amount_vat
            # En caso de no encontrar un impuesto, hago que el precio unitario sea la suma de neto gravado e IVA para
            # mantener el subtotal y total intactos
            else:
                line_vals['price_unit'] += self.amount_vat
            line_vals.update(base_vals)
            lines.append((0, 0, line_vals))
        # En caso de que AFIP informe un importe no gravado, agrego una línea para el mismo
        if self.amount_not_taxed:
            not_taxed_tax = self._get_not_taxed_tax()
            line_vals = {'name': "No gravado", 'price_unit': self.amount_not_taxed, 'tax_ids': [(6, 0, not_taxed_tax.ids)]}
            line_vals.update(base_vals)
            lines.append((0, 0, line_vals))
        # En caso de que AFIP informe un importe exento, agrego una línea para el mismo
        if self.amount_exempt:
            exempt_tax = self._get_exempt_tax()
            line_vals = {'name': "Exento", 'price_unit': self.amount_exempt, 'tax_ids': [(6, 0, exempt_tax.ids)]}
            line_vals.update(base_vals)
            lines.append((0, 0, line_vals))
        # Si me quedó una diferencia entre total vs. neto gravado + IVA + no gravado + exento, quiere decir que hay
        # impuestos adicionales (percepciones, impuestos internos, etc.) - Como no tengo forma de saber qué impuestos
        # son, agrego esa diferencia como una línea adicional sin impuestos para que el total de la factura coincida
        # con el del Excel
        diff = round(self.amount_total - self.amount_untaxed - self.amount_vat - self.amount_not_taxed - self.amount_exempt, 2)
        if diff:
            line_vals = {'name': "Impuestos varios", 'price_unit': diff}
            line_vals.update(base_vals)
            lines.append((0, 0, line_vals))

        return lines
    
    def _get_vat_tax(self, percentage):
        if not percentage:
            return False
        return self.env['account.tax'].sudo().search([
            ('company_id', '=', self.wizard_id.company_id.id),
            ('is_exempt', '=', False),
            ('is_vat', '=', True),
            ('amount_type', '=', 'percent'),
            ('amount', '=', percentage),
            ('type_tax_use', '=', 'purchase' if self.wizard_id.type == 'received' else 'sale')
        ], limit=1)

    def _get_not_taxed_tax(self):
        tax = self.env['account.tax'].sudo().search([
            ('company_id', '=', self.wizard_id.company_id.id),
            ('is_exempt', '=', True),
            ('is_vat', '=', False),
            ('amount', '=', 0.0),
            ('amount_type', '=', 'fixed'),
            ('type_tax_use', '=', 'purchase' if self.wizard_id.type == 'received' else 'sale')
        ], limit=1)
        if not tax:
            raise ValidationError("No se encontró impuesto para Iva No Gravado")
        return tax

    def _get_exempt_tax(self):
        tax = self.env['account.tax'].sudo().search([
            ('company_id', '=', self.wizard_id.company_id.id),
            ('is_exempt', '=', True),
            ('is_vat', '=', True),
            ('type_tax_use', '=', 'purchase' if self.wizard_id.type == 'received' else 'sale')
        ], limit=1)
        if not tax:
            raise ValidationError("No se encontró impuesto para Iva Exento")
        return tax

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
