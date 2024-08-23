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
            lambda i: i.type in ['in_invoice', 'in_refund']
            and i.voucher_type_id.is_importation_forward and (i.voucher_name or i.importation_forward_number) and i.voucher_type_id.denomination_id == self.data.type_d
        )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
