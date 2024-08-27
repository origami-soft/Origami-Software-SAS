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

from odoo import models, api
from odoo.exceptions import ValidationError
from l10n_ar_api.presentations import presentation


class InvoiceAfipPresentation(models.AbstractModel):

    _name = 'invoice.afip.presentation'
    _description = 'Presentacion de facturas para afip'

    def get_period(self):
        """
        Genera un string con el periodo seleccionado.
        :return: string con periodo ej : '201708'
        """
        split_from = self.date_from.strftime('%Y-%m-%d').split('-')
        return split_from[0] + split_from[1]

    def get_domain_invoices(self):
        """ Obtengo el dominio con las condiciones para buscar las facturas"""
        return [
            ('state', '=', 'posted'),
            ('voucher_type_id', '!=', False),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('company_id', '=', self.company_id.id),
        ]

    def get_invoices(self):
        return self.env['account.move'].search(self.get_domain_invoices()).filtered(lambda x: x.is_invoice())

    def validate_invoices(self, data):
        """
        Validamos que las facturas tengan los datos necesarios.
        """

        foreign_fiscal_positions = [
            self.env.ref('l10n_ar_afip_tables.account_fiscal_position_cliente_ext'),
            self.env.ref('l10n_ar_afip_tables.account_fiscal_position_prov_ext'),
        ]

        errors = []

        for invoice in self.invoices:
            if not invoice.fiscal_position_id:
                errors.append("La factura {} no posee posicion fiscal.".format(invoice.name))

            is_foreign = invoice.fiscal_position_id in foreign_fiscal_positions

            if not invoice.partner_id.vat and not is_foreign:
                errors.append("El partner {} no posee numero de documento.".format(invoice.partner_id.name))

            if not invoice.partner_id.partner_document_type_id:
                errors.append("El partner {} no posee tipo de documento.".format(invoice.partner_id.name))

            if not invoice.partner_id.country_id.vat and is_foreign and \
                    invoice.partner_id.country_id != invoice.partner_id.env.ref('base.ar'):
                errors.append("El partner {} no posee pais con documento.".format(invoice.partner_id.name))

            if invoice.amount_total == 0:
                errors.append("El total de la factura {} es cero.".format(invoice.name))

            if not invoice.line_ids:
                errors.append("La factura {} no posee lineas de asientos.".format(invoice.name))

            if self.get_total_notTaxed_taxes(invoice, data):
                errors.append("La factura {} posee montos en los impuestos no gravados.".format(invoice.name))

        if errors:
            raise ValidationError(
                "ERROR\nLa presentacion no pudo ser generada por los siguientes motivos:\n{}".format("\n".join(errors))
            )

    @staticmethod
    def get_total_notTaxed_taxes(invoice, data):
        return invoice.line_ids.filtered(
            lambda t: t.tax_line_id in [data.tax_sale_ng, data.tax_purchase_ng] and (t.debit or t.credit)
        )

    @staticmethod
    def generate_reginfo_zip_file(files):
        """
        Instancia el exportador en zip de ficheros de la API, y exporta todas las presentaciones.
        :param files: generators de las presentaciones
        :return: archivo zip
        """
        exporter = presentation.PresentationZipExporter()
        for file in files:
            exporter.add_element(file)
        return exporter.export_elements()

    @api.constrains('date_from', 'date_to')
    def check_dates(self):
        if self.date_from > self.date_to:
            raise ValidationError("La fecha 'desde' no puede ser mayor a la fecha 'hasta'.")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
