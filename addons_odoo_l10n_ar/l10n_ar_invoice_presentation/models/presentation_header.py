# - coding: utf-8 -*-

from odoo.exceptions import UserError
from odoo import models
import l10n_ar_api.presentations.presentation as presentation_builder


class AccountInvoicePresentation(models.Model):
    _inherit = 'account.invoice.presentation'

    def validate_header(self):
        """
        Validamos que la compania tenga los datos necesarios.
        """
        if not self.company_id.partner_id.vat:
            raise UserError(
                "ERROR\nLa presentacion no pudo ser generada porque la compania no tiene CUIT\n"
            )

    def generate_header_file(self):
        """
        Se genera el archivo de cabecera. Utiliza la API de presentaciones y tools para poder crear los archivos
        y formatear los datos.
        :return: objeto de la api (generator), con las lineas de la presentacion creadas.
        """
        self.validate_header()

        cabecera = presentation_builder.Presentation("ventasCompras", "cabecera")
        line = cabecera.create_line()

        line.cuit = self.company_id.vat
        line.periodo = self.get_period()
        line.secuencia = self.sequence
        line.sinMovimiento = 'S'
        if self.with_prorate:
            line.prorratearCFC = 'S'
            line.cFCGlobal = '1'
        else:
            line.prorratearCFC = 'N'
            line.cFCGlobal = '2'
        line.importeCFCG = 0
        line.importeCFCAD = 0
        line.importeCFCP = 0
        line.importeCFnCG = 0
        line.cFCSSyOC = 0
        line.cFCCSSyOC = 0

        return cabecera

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

