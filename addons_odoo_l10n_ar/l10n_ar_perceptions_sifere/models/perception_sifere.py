# -*- encoding: utf-8 -*-

from l10n_ar_api.presentations import presentation
from odoo import models


class PerceptionSifere(models.Model):
    _name = 'perception.sifere'
    _inherit = 'txt.report'
    _description = 'Percepción SIFERE'

    def get_code(self, p):
        return self.env['codes.models.relation'].get_code(
            'res.country.state',
            p.perception_id.state_id.id,
            'ConvenioMultilateral'
        )

    def _get_invoice_currency_rate(self, invoice):
        rate = 1
        if invoice.line_ids:
            move = invoice.line_ids[0]
            if move.amount_currency:
                rate = abs((move.credit + move.debit) / move.amount_currency)
        return rate
    
    def _get_tipo(self, p):
        if p.move_id.move_type in ['in_invoice', 'in_refund'] and \
                p.move_id.voucher_type_id.denomination_id == self.env.ref('l10n_ar_afip_tables.account_denomination_o'):
            return 'O'
        elif p.move_id.move_type == 'in_invoice':
            return 'D' if p.move_id.voucher_type_id.is_debit_note else 'F'
        return 'C'

    def _get_denomination(self, p):
        if p.move_id.move_type in ['in_invoice', 'in_refund'] and \
                p.move_id.voucher_type_id.denomination_id == self.env.ref('l10n_ar_afip_tables.account_denomination_o'):
            return ' '
        return p.move_id.voucher_type_id.denomination_id.name

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
        if not self.get_code(perception):
            errors.append(f'La jurisdicción {perception.state_id.name} no posee código')
        split_voucher_name = invoice.voucher_name.split('-')
        if split_voucher_name and any(not l.isdigit() for l in split_voucher_name):
            errors.append(f"La factura {invoice.full_voucher_name} contiene caracteres inválidos (solamente se permiten números y guiones)")

        return errors
    
    def get_model(self):
        return self.env['account.invoice.perception']
    
    def get_domain(self):
        invalid_denomination = self.env.ref('l10n_ar_afip_tables.account_denomination_d').id
        return [
            ('move_id.voucher_type_id', '!=', False),
            ('move_id.date', '>=', self.date_from),
            ('move_id.date', '<=', self.date_to),
            ('perception_id.type', '=', 'gross_income'),
            ('move_id.voucher_type_id.denomination_id', '!=', invalid_denomination),
            ('move_id.state', '=', 'posted'),
            ('perception_id.type_tax_use', '=', 'purchase'),
            ('move_id.company_id', '=', self.company_id.id)
        ]
    
    def sort_records(self, records):
        return records.sorted(key=lambda r: (r.move_id.date, r.id))
    
    def get_presentation(self):
        return presentation.Presentation("sifere", "percepciones")
    
    def get_filename(self):
        return f"per_iibb_{str(self.date_from).replace('-', '')}_{str(self.date_to).replace('-', '')}.txt"

    def create_line(self, lines, r):
        factor = 1
        if r.move_id.move_type in ['out_refund', 'in_refund']:
            factor = -1
        line = lines.create_line()
        line.jurisdiccion = self.get_code(r)
        vat = r.move_id.partner_id.vat
        line.cuit = "{0}-{1}-{2}".format(vat[0:2], vat[2:10], vat[-1:])
        line.fecha = (r.move_id.date or r.move_id.invoice_date).strftime('%d/%m/%Y')
        split_voucher_name = r.move_id.voucher_name.split('-')
        line.puntoDeVenta = split_voucher_name[0][-4:] if len(split_voucher_name) > 1 else '0'.zfill(4)
        line.numeroComprobante = split_voucher_name[1][:8] if len(split_voucher_name) > 1 else r.move_id.voucher_name[-8:]
        line.tipo = self._get_tipo(r)
        line.letra = self._get_denomination(r)
        line.importe = '{0:.2f}'.format(r.amount * self._get_invoice_currency_rate(r.move_id) * factor).replace('.', ',')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
