# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from l10n_ar_api.presentations import presentation
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PerceptionSifere(models.Model):
    _name = 'perception.sifere'
    _description = 'Percepción sifere'

    def _get_invoice_currency_rate(self, invoice):
        rate = 1
        if invoice.line_ids:
            move = invoice.line_ids[0]
            if move.amount_currency:
                rate = abs((move.credit + move.debit) / move.amount_currency)
        return rate

    def _get_tipo(self, p):
        if p.move_id.type in ['in_invoice', 'in_refund'] and \
                p.move_id.voucher_type_id.denomination_id == self.env.ref('l10n_ar_afip_tables.account_denomination_o'):
            return 'O'
        elif p.move_id.type == 'in_invoice':
            return 'D' if p.move_id.voucher_type_id.is_debit_note else 'F'
        else:
            return 'C'

    def _get_denomination(self, p):
        if p.move_id.type in ['in_invoice', 'in_refund'] and \
                p.move_id.voucher_type_id.denomination_id == self.env.ref('l10n_ar_afip_tables.account_denomination_o'):
            return ' '
        else:
            return p.move_id.voucher_type_id.denomination_id.name

    def _get_invalid_denomination(self):
        return self.env.ref('l10n_ar_afip_tables.account_denomination_d').name

    def get_code(self, p):
        return self.env['codes.models.relation'].get_code(
            'res.country.state',
            p.perception_id.state_id.id,
            'ConvenioMultilateral'
        )

    def partner_document_type_not_cuit(self, partner):
        return partner.partner_document_type_id != self.env.ref('l10n_ar_afip_tables.partner_document_type_80')

    def create_line(self, code, lines, p):
        factor = 1
        if p.move_id.type in ['out_refund', 'in_refund']:
            factor = -1
        line = lines.create_line()
        line.jurisdiccion = code
        vat = p.move_id.partner_id.vat
        line.cuit = "{0}-{1}-{2}".format(vat[0:2], vat[2:10], vat[-1:])
        line.fecha = (p.move_id.date or p.move_id.invoice_date).strftime('%d/%m/%Y')
        split_voucher_name = p.move_id.voucher_name.split('-')
        if split_voucher_name and any(not l.isdigit() for l in split_voucher_name):
            msg = "La factura {} contiene caracteres inválidos (solamente se permiten números y guiones)"
            raise ValidationError(msg.format(p.move_id.name))
        line.puntoDeVenta = split_voucher_name[0][-4:] if len(split_voucher_name) > 1 else '0'.zfill(4)
        line.numeroComprobante = split_voucher_name[1][:8] if len(split_voucher_name) > 1 else p.move_id.voucher_name[-8:]
        line.tipo = self._get_tipo(p)
        line.letra = self._get_denomination(p)
        line.importe = '{0:.2f}'.format(p.amount * self._get_invoice_currency_rate(p.move_id) * factor).replace('.', ',')

    def generate_file(self):
        lines = presentation.Presentation("sifere", "percepciones")
        perceptions = self.env['account.invoice.perception'].search([
            ('move_id.voucher_type_id', '!=', False),
            ('move_id.date', '>=', self.date_from),
            ('move_id.date', '<=', self.date_to),
            ('perception_id.type', '=', 'gross_income'),
            ('move_id.voucher_type_id.denomination_id.name', '!=', self._get_invalid_denomination()),
            ('move_id.state', '=', 'posted'),
            ('perception_id.type_tax_use', '=', 'purchase'),
            ('move_id.company_id', '=', self.company_id.id)
        ]).sorted(key=lambda r: (r.move_id.date, r.id))

        missing_vats = set()
        invalid_doctypes = set()
        invalid_vats = set()
        missing_codes = set()

        for p in perceptions:
            code = self.get_code(p)

            vat = p.move_id.partner_id.vat
            if not vat:
                missing_vats.add(p.move_id.name_get()[0][1])
            elif len(vat) < 11:
                invalid_vats.add(p.move_id.name_get()[0][1])
            if self.partner_document_type_not_cuit(p.move_id.partner_id):
                invalid_doctypes.add(p.move_id.name_get()[0][1])
            if not code:
                missing_codes.add(p.perception_id.state_id.name)

            # si ya encontro algun error, que no siga con el resto del loop porque el archivo no va a salir
            # pero que siga revisando las percepciones por si hay mas errores, para mostrarlos todos juntos
            if missing_vats or invalid_doctypes or invalid_vats or missing_codes:
                continue
            try:
                self.create_line(code, lines, p)
            except ValidationError as e:
                raise e
            except Exception as e:
                raise ValidationError(e)

        if missing_vats or invalid_doctypes or invalid_vats or missing_codes:
            errors = []
            if missing_vats:
                errors.append("Los partners de las siguientes facturas no poseen numero de CUIT:")
                errors.extend(missing_vats)
            if invalid_doctypes:
                errors.append("El tipo de documento de los partners de las siguientes facturas no es CUIT:")
                errors.extend(invalid_doctypes)
            if invalid_vats:
                errors.append("Los partners de las siguientes facturas poseen numero de CUIT erroneo:")
                errors.extend(invalid_vats)
            if missing_codes:
                errors.append("Las siguientes jurisdicciones no poseen codigo:")
                errors.extend(missing_codes)
            raise ValidationError("\n".join(errors))

        else:
            self.file = lines.get_encoded_string()
            self.filename = 'per_iibb_{}_{}.txt'.format(
                str(self.date_from).replace('-', ''),
                str(self.date_to).replace('-', '')
            )

    name = fields.Char(string='Nombre', required=True)
    date_from = fields.Date(string='Desde', required=True)
    date_to = fields.Date(string='Hasta', required=True)
    file = fields.Binary(string='Archivo', filename="filename")
    filename = fields.Char(string='Nombre Archivo')
    company_id = fields.Many2one(
        'res.company',
        string='Empresa',
        required=True,
        readonly=True,
        change_default=True,
        default=lambda self: self.env.company
    )

    @api.constrains('date_from', 'date_to')
    def check_date(self):
        if self.date_from > self.date_to:
            raise ValidationError("La fecha de inicio no puede ser mayor a la fecha fin.")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
