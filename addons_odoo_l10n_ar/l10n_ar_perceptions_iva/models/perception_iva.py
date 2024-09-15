# -*- encoding: utf-8 -*-

from l10n_ar_api.presentations import presentation
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PerceptionIva(models.Model):
    _name = 'perception.iva'
    _inherit = 'txt.report'
    _description = 'Percepción IVA'

    perception_code = fields.Integer(
        'Código regimen',
        help="Código de regimen usado para las percepciones",
        required=True
    )

    def _get_invoice_currency_rate(self, invoice):
        rate = 1
        if invoice.line_ids:
            move = invoice.line_ids[0]
            if move.amount_currency:
                rate = abs((move.credit + move.debit) / move.amount_currency)
        return rate
    
    def validate_fields(self, perception):
        errors = []
        invoice = perception.move_id
        partner = invoice.partner_id
        if not partner.vat:
            errors.append(f'El partner {partner.name} no posee número de documento')
        else:
            if len(partner.vat) < 11:
                errors.append(f'El partner {partner.name} posee un número de CUIT erróneo')
            if partner.partner_document_type_id != self.env.ref('l10n_ar_afip_tables.partner_document_type_80'):
                errors.append(f'El partner {partner.name} no posee CUIT como tipo de documento')
        if not invoice.voucher_type_id.is_importation_forward:
            split_voucher_name = invoice.voucher_name.split('-')
            if split_voucher_name and any(not l.isdigit() for l in split_voucher_name):
                errors.append(f"La factura {invoice.full_voucher_name} contiene caracteres inválidos (solamente se permiten números y guiones)")

        return errors
    
    def get_model(self):
        return self.env['account.invoice.perception']
    
    def get_domain(self):
        return [
            ('move_id.voucher_type_id', '!=', False),
            ('move_id.date', '>=', self.date_from),
            ('move_id.date', '<=', self.date_to),
            ('perception_id.type', '=', 'vat'),
            ('move_id.state', '=', 'posted'),
            ('perception_id.type_tax_use', '=', 'purchase'),
            ('move_id.company_id', '=', self.company_id.id)
        ]
    
    def sort_records(self, records):
        return records.sorted(key=lambda r: (r.move_id.date, r.id))
    
    def get_presentation(self):
        return presentation.Presentation("iva", "percepciones")
    
    def get_filename(self):
        return f"per_iva_{str(self.date_from).replace('-', '')}_{str(self.date_to).replace('-', '')}.txt"

    def create_line(self, lines, r):
        line = lines.create_line()
        invoice = r.move_id
        cuit = invoice.partner_id.vat
        line.cuit = f"{cuit[:2]}-{cuit[2:10]}-{cuit[-1:]}"
        line.fecha = (invoice.date or invoice.invoice_date).strftime(
            '%d/%m/%Y')
        if invoice.voucher_type_id.is_importation_forward:
            line.numeroDeFacturaUno = invoice.voucher_name[:8]
            line.numeroDeFacturaDos = invoice.voucher_name[8:]
        else:
            split_voucher_name = invoice.voucher_name.split('-')
            if len(split_voucher_name) > 1:
                line.numeroDeFacturaUno = split_voucher_name[0]
                line.numeroDeFacturaDos = split_voucher_name[1]
            else:
                line.numeroDeFacturaUno = split_voucher_name[:4]
                line.numeroDeFacturaDos = split_voucher_name[-8:]
        line.monto = '{0:.2f}'.format(
            r.amount * self._get_invoice_currency_rate(invoice)).replace('.', ',')

        line.codigoDePercepcion = self.perception_code

    @api.constrains('perception_code')
    def check_length_perception_code(self):
        if 100 > self.perception_code or self.perception_code > 999:
            raise ValidationError(
                'El código de percepcion debe ser de 3 dígitos')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
