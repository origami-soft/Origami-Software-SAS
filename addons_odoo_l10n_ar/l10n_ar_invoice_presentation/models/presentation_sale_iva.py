# coding: utf-8

from .presentation import SalePresentation


class SaleVatInvoicePresentation(SalePresentation):
    def __init__(self, builder, data):
        super(SaleVatInvoicePresentation, self).__init__(builder=builder, data=data)

    def filter_invoices(self, invoices):
        """
        Trae las facturas para generar la presentacion de alicuotas de ventas.
        :return: recordset, Las facturas de compras.
        """
        return invoices.filtered(
            lambda i: i.move_type in ["out_invoice", "out_refund"]
        )

    def create_line(self, invoice):
        """
        Crea una linea por cada factura, usando el builder y el helper
        :param invoice: record, factura
        """
        self.rate = invoice.get_currency_rate_from_move()

        tipoComprobante = self.get_tipo(invoice)
        puntoDeVenta = self.get_puntoDeVenta(invoice)
        numeroComprobante = self.get_numeroComprobante(invoice)

        invoice_vat_taxes = self.get_invoices_vat_taxes(invoice)

        for tax in invoice_vat_taxes:
            line = self.builder.create_line()

            line.tipoComprobante = tipoComprobante
            line.puntoDeVenta = puntoDeVenta
            line.numeroComprobante = numeroComprobante
            line.importeNetoGravado = self.get_importeNetoGravado(invoice, tax)
            line.alicuotaIva = self.get_alicuotaIva(tax)
            line.impuestoLiquidado = self.get_impuestoLiquidado(tax)

        # En caso que no tenga ningun impuesto, se informa una alicuota por defecto (Iva 0%)
        if not invoice_vat_taxes:
            line = self.builder.create_line()
            line.tipoComprobante = tipoComprobante
            line.puntoDeVenta = puntoDeVenta
            line.numeroComprobante = numeroComprobante
            line.importeNetoGravado = '0'
            line.alicuotaIva = '3'
            line.impuestoLiquidado = '0'

    # ----------------CAMPOS ALICUOTAS----------------
    def get_importeNetoGravado(self, invoice, tax):
        """
        Obtiene el neto gravado de la operacion. Para los impuestos exentos o no gravados devuelve 0.
        :param tax: objeto impuesto
        :return: string, monto del importe
        """
        if tax.tax_line_id.is_exempt or tax.tax_line_id == self.data.tax_sale_ng:
            return '0'

        base = sum(
            invoice.invoice_line_ids.filtered(
                lambda x: tax.tax_line_id in x.tax_ids
            ).mapped('price_subtotal')
        )

        return self.helper.format_amount(base)

    def get_alicuotaIva(self, tax):
        """
        Si el impuesto es exento o no gravado, la alicuota a informar es la de 0%, y su codigo es 3,
        ya que el SIAP no contempla los codigos 1(no gravado) ni 2(exento).
        :param tax: objeto impuesto
        """
        if tax.tax_line_id.is_exempt or tax.tax_line_id == self.data.tax_sale_ng:
            return '3'

        return super(SaleVatInvoicePresentation, self).get_alicuotaIva(tax)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
