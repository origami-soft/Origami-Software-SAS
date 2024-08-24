# - coding: utf-8 -*-

from odoo import models
import l10n_ar_api.presentations.presentation as presentation_builder


class AccountInvoicePresentation(models.Model):
    _inherit = 'account.invoice.presentation'

    def generate_fiscal_credit_service_import_file(self):
        """
        Se genera el archivo de credito fiscal de servicios. No se encuentra implementado.
        """
        fiscal_credit_file = presentation_builder.Presentation("ventasCompras", "creditoFiscalImportacionServ")

        return fiscal_credit_file


class AccountInvoiceVatDigitalBook(models.Model):
    _inherit = 'account.invoice.vat.digital.book'

    def generate_fiscal_vat_digital_book_credit_service_import_file(self):
        """
        Se genera el archivo de credito fiscal de servicios. No se encuentra implementado.
        """
        fiscal_credit_file = presentation_builder.Presentation("libroIVADigital", "creditoFiscalImportacionServ")

        return fiscal_credit_file

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

