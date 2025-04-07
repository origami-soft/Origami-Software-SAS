# -*- encoding: utf-8 -*-

from l10n_ar_api.presentations import presentation
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class RetentionIva(models.Model):
    _name = "retention.iva"
    _inherit = 'txt.report'
    _description = "Retenciones IVA"

    def partner_document_type_not_cuit(self, partner):
        return partner.partner_document_type_id != self.env.ref(
            "l10n_ar_afip_tables.partner_document_type_80"
        )

    def create_line(self, lines, retention_id):
        payment_id = retention_id.payment_id
        # Elimino los guiones insertados en el certificado para luego verificar el largo del mismo
        certificate_no = retention_id.certificate_no.replace("-", "")
        if len(certificate_no) > 16:
            raise ValidationError(f"El número de certificado de la retención {retention_id.name} en el pago {payment_id.name} excede en caracteres el maximo permitido")
        line = lines.create_line()
        cuit = payment_id.partner_id.vat
        line.cuit = f"{cuit[:2]}-{cuit[2:10]}-{cuit[-1:]}"
        line.fecha = (retention_id.date or payment_id.date).strftime("%d/%m/%Y")
        line.numeroDeComprobante = certificate_no
        line.monto = "{0:.2f}".format(retention_id.amount).replace(".", ",")
        line.codigoDeRetencion = self.retention_code

    def get_model(self):
        return self.env['account.payment.retention']

    def get_domain(self):
        return [
            ("payment_id.voucher_type_id", "!=", False),
            ("payment_id.date", ">=", self.date_from),
            ("payment_id.date", "<=", self.date_to),
            ("retention_id.type", "=", "vat"),
            ("payment_id.state", "=", "posted"),
            ("retention_id.type_tax_use", "=", "sale"),
            ("payment_id.company_id", "=", self.company_id.id),
        ]

    def sort_records(self, records):
        return records.sorted(key=lambda r: (r.payment_id.date, r.id))

    def get_presentation(self):
        return presentation.Presentation("iva", "retenciones")

    def get_filename(self):
        return f"ret_iva_{str(self.date_from).replace('-', '')}_{str(self.date_to).replace('-', '')}.txt"

    
    def validate_fields(self, retention):
        errors = []
        payment_id = retention.payment_id
        partner_id = payment_id.partner_id
        if not partner_id.vat:
            errors.append(f'El partner {partner_id.name} no posee número de documento')
        else:
            if len(partner_id.vat) < 11:
                errors.append(f'El partner {partner_id.name} posee un número de CUIT erróneo')
            if partner_id.partner_document_type_id != self.env.ref('l10n_ar_afip_tables.partner_document_type_80'):
                errors.append(f'El partner {partner_id.name} no posee CUIT como tipo de documento')
        if not payment_id.voucher_type_id.is_importation_forward:
            split_voucher_name = payment_id.voucher_name.split('-')
            if split_voucher_name and any(not l.isdigit() for l in split_voucher_name):
                errors.append(f"El pago {payment_id.display_name} contiene caracteres inválidos (solamente se permiten números y guiones)")

        return errors

    name = fields.Char(string="Nombre", required=True)
    retention_code = fields.Integer(
        "Código regimen de retención",
        help="Codigo de regimen usado para las retenciones",
        required=True,
    )

    @api.constrains("retention_code")
    def check_length_retention_code(self):
        if 100 > self.retention_code or self.retention_code > 999:
            raise ValidationError("El codigo de retención debe ser de 3 digitos")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
