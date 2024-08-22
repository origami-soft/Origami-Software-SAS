# -*- coding: utf-8 -*-

from odoo import http
from odoo.addons.account.controllers.portal import PortalAccount
from odoo.exceptions import AccessError, MissingError
from odoo.http import request


class ElectronicInvoicePortalAccount(PortalAccount):
    @http.route(['/my/invoices/<int:invoice_id>'], type='http', auth="public", website=True)
    def portal_my_invoice_detail(self, invoice_id, access_token=None, report_type=None, download=False, **kw):
        """ Piso la funcion base para pasarle el reporte de factura electronica si la factura lo es"""
        try:
            invoice_sudo = self._document_check_access('account.move', invoice_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            report = 'l10n_ar_electronic_invoice_report.action_electronic_invoice' \
                if invoice_sudo.document_book_id.book_type_id.is_electronic() else 'account.account_invoices'
            # Si estoy imprimiendo una FE sin CAE (no validada) o una vista previa en HTML, activo la previsualización
            # (ya que si quiero imprimir una FE normalmente no me deja por la validación de CAE, y las vistas previas
            # en HTML salen mal si el talonario está configurado para imprimir duplicados)
            if not invoice_sudo.cae or report_type == 'html':
                context = request.env.context.copy()
                context.update({'previsualize_invoices': True})
                request.env.context = context
            return self._show_report(model=invoice_sudo, report_type=report_type, report_ref=report, download=download)

        return super(ElectronicInvoicePortalAccount, self).portal_my_invoice_detail(invoice_id, access_token, report_type, download, **kw)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
