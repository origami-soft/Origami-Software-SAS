# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from l10n_ar_api.presentations import presentation


class RetentionSicore(models.Model):
    _name = "retention.sicore"
    _inherit = 'txt.report'
    _description = 'Retención SICORE'

    def validate_fields(self, retention):
        errors = []
        payment = retention.payment_id
        partner = payment.partner_id
        if not payment.voucher_name:
            errors.append(f'El pago {payment.name} no posee un número válido para su presentación en SICORE')
        if not partner.vat:
            errors.append(f'El partner {partner.name} no posee número de documento')
        else:
            if len(partner.vat) < 11:
                errors.append(f'El partner {partner.name} posee un número de CUIT erróneo')
            try:
                document_afip_code = self.env['codes.models.relation'].get_code(
                    'partner.document.type',
                    partner.partner_document_type_id.id,
                    'Afip'
                )
            except ValidationError:
                errors.append(f'El partner {partner.name} no posee tipo de documento válido')

        if retention.activity_id and not retention.activity_id.code:
            errors.append(f'La actividad {retention.activity_id.name} no posee código de regimen')
        return errors
    
    def get_model(self):
        return self.env['account.payment.retention']

    def get_domain(self):
        return [
            ('payment_id.voucher_type_id', '!=', False),
            ('payment_id.journal_id.payment_usage', '=', 'document_book'),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('type', 'in', ('profit', 'vat')),
            ('payment_id.state', 'in', ['posted', 'reconciled']),
            ('payment_id.payment_type', '=', 'outbound'),
            ('payment_id.company_id', '=', self.company_id.id)
        ]

    def sort_records(self, retentions):
        return retentions.sorted(key=lambda r: (r.payment_id.date, r.certificate_no))

    def get_code(self, document):
        # CÓDIGO DE COMPROBANTE
        # 01 Factura
        # 02 Recibo
        # 03 Nota de Crédito
        # 04 Nota de Débito
        # 05 Otro comprobante
        # 06 Orden de Pago
        # 07 Recibo de Sueldo
        # 08 Recibo de Sueldo- Devolución
        # 09 Escritura Pública
        # 10 C.1116
        # 11 Factura (16 Dígitos)
        return '06' if document._name == 'account.payment' else ''

    def get_tax_code(self, retention):
        # CÓDIGO DE IMPUESTO
        # 064 Fondo Nacional de Incentivo Docente
        # 172 Impuesto a la Transferencia de Inmuebles
        # 210 Ganancias Régimen Especial de Ingreso R.G. 830
        # 217 Impuesto a las Ganancias
        # 218 Impuesto a las Ganancias - Beneficiarios del Exterior
        # 466 Gravamen de Emergencia a los Premios de determinados juegos de sorteoy concursos deportivos
        # 767 Impuesto al Valor Agregado
        return '767' if retention.type == 'vat' else '217'

    def get_condition_code(self):
        # CÓDIGO DE CONDICIÓN
        # 00 Ninguna
        # 01 Inscripto
        # 02 No inscripto.
        # 03 No categorizado
        # 06 Contratación hora día estadía
        # 07 Contratación mensual
        # 08 Incluido en el régimen fiscal de granos
        # 09 No incluido en el régimen fiscal de granos
        # 10 Inscripto demás sujetos
        # 11 Inscripto retenciones IVA estaciones de servicios
        # 12 Servicios públicos
        # 13 Venta de cosas muebles y locación - Alícuota general
        # 14 Venta de cosas muebles y locación - Alícuota reducida
        # 15 Retención sustitutiva
        return '01'

    def get_document_afip_code(self, document_id):
        return self.env['codes.models.relation'].get_code('partner.document.type', document_id, 'Afip')

    def create_line(self, lines, r):
        line = lines.create_line()
        line.codigoComprobante = self.get_code(r.payment_id)
        line.fechaDocumento = r.payment_id.date.strftime('%d/%m/%Y')
        line.referenciaDocumento = r.payment_id.voucher_name.replace('-', '').ljust(16)
        line.importeDocumento = '{0:.2f}'.format(r.payment_id.amount).zfill(16)
        line.codigoImpuesto = self.get_tax_code(r)
        line.codigoRegimen = str(r.activity_id.code).ljust(3) if r.activity_id else '865'
        line.codigoOperacion = '1'  # 1 Retención, 2 Percepción, 4 Imposibilidad de Retención
        line.base = '{0:.2f}'.format(r.base).zfill(14)
        line.fecha = r.date.strftime('%d/%m/%Y')
        line.codigoCondicion = self.get_condition_code()
        line.retencionPracticadaSS = '0'
        line.importe = '{0:.2f}'.format(r.amount).zfill(14)
        line.porcentaje = '{0:.2f}'.format(0).zfill(6)
        line.fechaEmision = ''.ljust(10)
        line.codigoDocumento = self.get_document_afip_code(r.payment_id.partner_id.partner_document_type_id.id)
        line.cuit = r.payment_id.partner_id.vat.ljust(20)
        line.numeroCertificado = r.certificate_no.replace('-', '').zfill(14)
    
    def get_presentation(self):
        return presentation.Presentation("sicore", "retenciones")

    def get_filename(self):
        return f"ret_gan_{str(self.date_from).replace('-', '')}_{str(self.date_to).replace('-', '')}.txt"

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
