# - coding: utf-8 -*-

from .presentation import PurchaseVatPresentation


class PurchaseImportationPresentation(PurchaseVatPresentation):
    def __init__(self, builder, data):
        super(PurchaseImportationPresentation, self).__init__(builder, data)

    def filter_invoices(self, invoices):
        """
        Trae las facturas para generar la presentacion de alicuotas de compras de importacion.

        NOTA IMPORTANTE: La variable importation_forward_number debe conservarse para mantener la retrocompatibilidad,
        pero no debe ser utilizada en nuevas versiones. En su lugar usar voucher_name.

        :return: recordset, Las facturas de compras.
        """
        return invoices.filtered(
            lambda i: i.move_type in ['in_invoice', 'in_refund']
            and i.voucher_type_id.is_importation_forward and (i.voucher_name or i.importation_forward_number) and i.voucher_type_id.denomination_id == self.data.type_d
        )

    def create_line(self, invoice):
        """
        Crea x lineas por cada factura, segun la cantidad de alicuotas usando el builder y el helper
        para todas las facturas de importacion.
        :param invoice: record, factura
        """
        self.rate = invoice.get_currency_rate_from_move()
        invoice_vat_taxes = self.get_invoices_vat_taxes(invoice)

        for tax in invoice_vat_taxes:
            importation_line = self.builder.create_line()

            importation_line.despachoImportacion = self.get_despachoImportacion(invoice)
            importation_line.importeNetoGravado = self.get_importeNetoGravado(invoice, tax)
            importation_line.alicuotaIva = self.get_alicuotaIva(tax)
            importation_line.impuestoLiquidado = self.helper.format_amount(abs(tax.balance))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
