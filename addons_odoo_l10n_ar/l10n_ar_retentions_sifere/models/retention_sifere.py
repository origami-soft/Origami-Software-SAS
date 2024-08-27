# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from l10n_ar_api.presentations import presentation


class RetentionSifere(models.Model):
    _name = 'retention.sifere'
    _inherit = 'txt.report'
    _description = 'Retención SIFERE'

    def get_code(self, r):
        return self.env['codes.models.relation'].get_code(
            'res.country.state',
            r.retention_id.state_id.id,
            'ConvenioMultilateral'
        )

    def create_line(self, lines, r):
        line = lines.create_line()
        line.jurisdiccion = self.get_code(r)
        vat = r.payment_id.partner_id.vat
        line.cuit = "{0}-{1}-{2}".format(vat[0:2], vat[2:10], vat[-1:])
        line.fecha = r.date.strftime('%d/%m/%Y')
        line.puntoDeVenta = r.payment_id.journal_id.pos_ar_id.name[-4:]
        line.numeroComprobante = ''.join([s for s in str(r.certificate_no) if s.isdigit()])[-16:]
        line.numeroBase = str(r.payment_id.name.split('-')[1] if '-' in str(r.payment_id.name) else r.payment_id.name)[:20]
        line.tipo = "R"
        line.letra = " "
        line.importe = '{0:.2f}'.format(r.amount).replace('.', ',')
    
    def get_model(self):
        return self.env['account.payment.retention']
    
    def get_domain(self):
        return [
            ('payment_id.voucher_type_id', '!=', False),
            ('payment_id.journal_id.payment_usage', '=', 'document_book'),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('retention_id.type', '=', 'gross_income'),
            ('payment_id.state', 'in', ['posted', 'reconciled']),
            ('payment_id.payment_type', '=', 'inbound'),
            ('payment_id.company_id', '=', self.company_id.id)
        ]
    
    def sort_records(self, retentions):
        return retentions.sorted(key=lambda r: (r.payment_id.date, r.id))
    
    def validate_fields(self, retention):
        errors = []
        payment = retention.payment_id
        partner = payment.partner_id
        if not partner.vat:
            errors.append(f'El partner {partner.name} no posee número de CUIT')
        elif len(partner.vat) < 11:
            errors.append(f'El partner {partner.name} posee un número de CUIT erróneo')
        if partner.partner_document_type_id != self.env.ref('l10n_ar_afip_tables.partner_document_type_80'):
            errors.append(f'El partner {partner.name} no posee tipo de documento CUIT')
        if not self.get_code(retention):
            errors.append(f'La jurisdicción {retention.state_id.name} no posee código')
        if not payment.journal_id.pos_ar_id:
            errors.append(f'El diario {payment.journal_id.name} no posee punto de venta')
        base_number = str(payment.name.split('-')[1] if '-' in str(payment.name) else payment.name)[:20]
        if not base_number.isdigit():
            errors.append(f"La orden de pago {payment.name} contiene caracteres inválidos (solamente se permiten números y guiones)")
        return errors
    
    def get_presentation(self):
        return presentation.Presentation("sifere", "retenciones")

    def get_filename(self):
        return f"ret_iibb_{str(self.date_from).replace('-', '')}_{str(self.date_to).replace('-', '')}.txt"

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
