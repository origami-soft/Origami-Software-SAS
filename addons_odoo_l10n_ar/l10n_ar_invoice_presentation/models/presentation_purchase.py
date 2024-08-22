# - coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from .presentation import PurchasePresentation


class PurchaseInvoicePresentation(PurchasePresentation):
    def __init__(self, with_prorate=False, builder=None, data=None):
        self.with_prorate = with_prorate
        super(PurchaseInvoicePresentation, self).__init__(builder=builder, data=data)

    def filter_invoices(self, invoices):
        """
        Trae las facturas para generar la presentacion de compras.
        :return: recordset, Las facturas de compras.
        """
        return invoices.filtered(
            lambda i: i.type in ['in_invoice', 'in_refund']
                      and i.voucher_type_id.denomination_id not in [
                self.data.type_d,
                self.data.type_i
            ]
        )

    def create_line(self, invoice):
        """
        Crea una linea por cada factura, usando el builder y el helper
        :param invoice: record, factura
        """
        self.rate = invoice.get_currency_rate_from_move()

        line = self.builder.create_line()

        line.fecha = self.get_fecha(invoice)
        line.tipo = self.get_tipo(invoice)
        line.puntoDeVenta = self.get_puntoDeVenta(invoice)
        line.numeroComprobante = self.get_numeroComprobante(invoice)
        line.despachoImportacion = self.get_despachoImportacion(invoice)
        line.codigoDocumento = self.get_codigoDocumento(invoice)
        line.numeroVendedor = self.get_numeroPartner(invoice)
        line.denominacionVendedor = self.get_denominacionPartner(invoice)
        line.importeTotal = self.get_importeTotal(invoice)
        line.importeTotalNG = self.get_importeTotalNG_purchase(invoice)
        line.importeOpExentas = self.get_importeOpExentas(invoice)
        line.importePerOIva = self.get_importe_per_by_type(invoice, ['vat'])
        line.importePerOtrosImp = self.get_importe_per_by_type(invoice, ['profit', 'other'])
        line.importePerIIBB = self.get_importe_per_by_type(invoice, ['gross_income'])
        line.importePerIM = self.get_importe_per_by_jurisdiction(invoice, ['municipal'])
        line.importeImpInt = self.get_importeImpInt(invoice)
        line.codigoMoneda = self.get_codigoMoneda(invoice)
        line.tipoCambio = self.get_tipoCambio()
        line.cantidadAlicIva = self.get_cantidadAlicIva(invoice)
        line.codigoOperacion = self.get_codigoOperacion(invoice)
        line.credFiscComp = self.get_credFiscComp(invoice)
        line.otrosTrib = self.get_otrosTrib(invoice)
        line.cuitEmisor = self.get_purchase_cuitEmisor(invoice)
        line.denominacionEmisor = self.get_purchase_denominacionEmisor(invoice)
        line.ivaComision = self.get_purchase_ivaComision()

    # ----------------CAMPOS COMPRAS----------------


    def get_importeOpExentas(self, invoice):
        """
        Devuelve el monto total de importes de operaciones exentas.
        :param invoice: record.
        :return: string, monto ej: 23.00-> '2300'
        """
        if invoice.voucher_type_id.denomination_id in [self.data.type_b, self.data.type_c]:
            return '0'
        return super(PurchaseInvoicePresentation, self).get_importeOpExentas(invoice)

    def get_cantidadAlicIva(self, invoice):
        """
        En caso de ser comprobante B o C se devuelve 0. Si la operacion es no gravada, se devuelve la cantidad
        de impuestos no gravado.
        :param invoice: record.
        """
        if invoice.voucher_type_id.denomination_id in [self.data.type_b, self.data.type_c]:
            return 0
        return super(PurchaseInvoicePresentation, self).get_cantidadAlicIva(invoice)

    def get_credFiscComp(self, invoice):
        """
        Se devuelve cero en caso de que no tenga alicuotas de iva. Si tiene alicuotas y la presentacion es
        sin prorrateo, se devuelven todos los impuestos. En caso contrario se devuelve la suma de los impuestos
        de iva.
        :param invoice: record.
        :return: string, ej: '0023'
        """
        # Si la cantidad de alicuotas es igual a 0, se devuelve 0
        if self.get_cantidadAlicIva(invoice) is 0:
            return self.helper.format_amount(0)
        # Sino se devuelve el monto de los impuestos de iva
        else:
            lines = invoice.line_ids.filtered(
                lambda t: t.tax_line_id.is_vat and t.tax_line_id != self.data.tax_purchase_ng and not t.tax_line_id.is_exempt
            )
            vat_tax_amount = sum(abs(line.amount_currency or line.balance) for line in lines)
            return self.helper.format_amount(vat_tax_amount)

    # No implementado


    # ----------------IMPLEMENTADO----------------------------------
    @staticmethod
    def get_purchase_cuitEmisor(invoice):
        if invoice.voucher_type_id.code in (60,61):
            return invoice.company_id.vat
        return 0

    # ----------------IMPLEMENTADO----------------------------------
    @staticmethod
    def get_purchase_denominacionEmisor(invoice):
        if invoice.voucher_type_id.code in (60,61):
            return invoice.company_id.name
        return ''

    @staticmethod
    def get_purchase_ivaComision():
        return 0

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
