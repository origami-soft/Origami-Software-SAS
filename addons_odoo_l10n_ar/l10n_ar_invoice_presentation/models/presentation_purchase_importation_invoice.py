# - coding: utf-8 -*-

from .presentation_purchase import PurchaseInvoicePresentation


class PurchaseImportationInvoicePresentation(PurchaseInvoicePresentation):
    def filter_invoices(self, invoices):
        """
        Trae las facturas para generar la presentacion de compras de importación.

        NOTA IMPORTANTE: La variable importation_forward_number debe conservarse para mantener la retrocompatibilidad,
        pero no debe ser utilizada en nuevas versiones. En su lugar usar voucher_name.

        :return: recordset con las facturas de compras.
        """
        return invoices.filtered(
            lambda i: i.move_type in ['in_invoice', 'in_refund']
            and i.voucher_type_id.is_importation_forward and (i.voucher_name or i.importation_forward_number) and i.voucher_type_id.denomination_id == self.data.type_d
        )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
