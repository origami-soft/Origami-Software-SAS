# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    perception_ids = fields.One2many(
        'account.invoice.perception',
        'move_id',
        string='Percepciones',
        copy=True
    )

    def action_post(self):
        for r in self.filtered(lambda l: l.move_type.startswith('out') and l.perception_ids):
            for t in r.perception_ids.mapped('perception_id').get_taxes(r.company_id):
                perc = sum(r.perception_ids.filtered(lambda l: l.perception_id and l.perception_id.get_taxes(r.company_id) == t).mapped('amount'))
                line = sum(r.line_ids.filtered(lambda l: l.tax_line_id == t).mapped(lambda l: abs(l.amount_currency)))
                if round(perc, 2) != round(line, 2):
                    raise ValidationError(f"Los importes declarados en {t.name} no coinciden con los de la factura.")
        return super().action_post()

    def get_perception_base(self):
        """ Obtengo la base sobre la cual voy a calcular las percepciones """
        self.ensure_one()
        return round(sum(self.invoice_line_ids.filtered(lambda l: l.perception_applies()).mapped('price_subtotal')), 2)

    @api.onchange('invoice_line_ids', 'currency_id', 'currency_rate')
    def onchange_set_perception_values(self):
        if self.move_type in ['out_invoice', 'out_refund']:
            perc_base = self.get_perception_base()
            for perception in self.perception_ids:
                perception.base = perc_base
                perception.onchange_aliquot()

    @api.onchange('perception_ids')
    def onchange_perception_ids(self):
        """ Para el caso que se borre una percepcion de la grilla de percepciones """
        taxes_invoices = self.invoice_line_ids.mapped('tax_ids').filtered(lambda x: x.amount_type == 'perception')
        perception_taxes = self.perception_ids.mapped('perception_id').get_taxes(self.company_id)
        # En caso de que haya percepciones a borrar, las desvinculo de las líneas
        taxes_to_unlink = taxes_invoices - perception_taxes
        self.invoice_line_ids.update({'tax_ids': [fields.Command.unlink(t.id) for t in taxes_to_unlink]})
        # En caso de que haya percepciones a agregar, las vinculo a las líneas que correspondan
        taxes_to_link = perception_taxes - taxes_invoices
        self.invoice_line_ids.filtered(lambda x: x.perception_applies()).update(
            {'tax_ids': [fields.Command.link(t.id) for t in taxes_to_link]})
    
    def get_perception_ctx(self):
        vals = {}
        for p in self.perception_ids:
            tax = p.perception_id.get_taxes(self.company_id)
            if not tax:
                raise ValidationError(f"No hay impuesto que contenga la percepción {p.name}\nPor favor asociar la percepción al impuesto correspondiente en la configuración de impuestos")
            elif len(tax) > 1:
                raise ValidationError(f"Hay más de un impuesto que tiene configurada la percepción {p.name}\nPor favor revisar la configuración de los impuestos {', '.join(tax.mapped('name'))}")
            vals[tax] = p.amount
        return vals
    
    @api.depends(
        'perception_ids.perception_id',
        'perception_ids.amount',
    )
    def _compute_tax_totals(self):
        """ Heredo el método que computa el resumen de impuestos al pie de la factura para pasarle por contexto el
        importe de cada percepción, a fin de que las incluya en el resumen de manera correcta
        """
        for r in self:
            super(AccountMove, r.with_context(perception_ctx=r.get_perception_ctx()))._compute_tax_totals()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
