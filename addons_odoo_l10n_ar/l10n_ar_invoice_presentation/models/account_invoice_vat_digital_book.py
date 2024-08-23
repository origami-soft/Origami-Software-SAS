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

from odoo import models, fields
from datetime import datetime
from l10n_ar_api.presentations import presentation
from .general_data import GeneralData
from .presentation_purchase import PurchaseInvoicePresentation
from .presentation_purchase_iva import PurchaseIvaPresentation
from .presentation_purchase_importation import PurchaseImportationPresentation
from .presentation_purchase_importation_invoice import PurchaseImportationInvoicePresentation
from .presentation_sale import SaleInvoicePresentation
from .presentation_sale_iva import SaleVatInvoicePresentation


class AccountInvoiceVatDigitalBook(models.Model):
    _name = 'account.invoice.vat.digital.book'
    _inherit = 'invoice.afip.presentation'
    _description = 'Libro IVA Digital'


    def generate_presentations(self, data):
        purchase_builder = presentation.Presentation('libroIVADigital', 'comprasCbte')
        purchase_iva_builder = presentation.Presentation('libroIVADigital', 'comprasAlicuotas')
        purchase_import_builder = presentation.Presentation('libroIVADigital', 'comprasImportaciones')
        purchase_import_invoice_builder = presentation.Presentation('libroIVADigital', 'comprasCbte')
        sale_builder = presentation.Presentation('libroIVADigital', 'ventasCbte')
        sale_iva_builder = presentation.Presentation('libroIVADigital', 'ventasAlicuotas')

        self.purchase_presentation = self.get_instance_presentation(class_name='purchase_presentation', data=data, builder=purchase_builder, with_prorate=self.with_prorate)
        self.purchase_iva_presentation = self.get_instance_presentation(class_name='purchase_iva_presentation', data=data, builder=purchase_iva_builder)
        self.purchase_import_presentation = self.get_instance_presentation(class_name='purchase_import_presentation', data=data, builder=purchase_import_builder)
        self.purchase_import_invoice_presentation = self.get_instance_presentation(class_name='purchase_import_invoice_presentation', data=data, builder=purchase_import_invoice_builder)
        self.sale_presentation = self.get_instance_presentation(class_name='sale_presentation', data=data, builder=sale_builder)
        self.sale_iva_presentation = self.get_instance_presentation(class_name='sale_iva_presentation', data=data, builder=sale_iva_builder)

    def generate_files(self):
        """
        Genera todas las presentaciones para el libro de IVA digital. A cada archivo generado le pone un nombre que se usa para
        crear el nombre del fichero. Luego llama a la funcion que colocara todos los archivos en
        un fichero zip.
        """
        # Traemos datos generales
        invoice_proxy = self.env['account.move']
        data = GeneralData(invoice_proxy, self.company_id)

        # Traemos y validamos todas las facturas del periodo seleccionado
        self.invoices = self.get_invoices()
        self.validate_invoices(data)

        # Instanciamos presentaciones
        self.generate_presentations(data)

        # Creamos nombre base para los archivos
        base_name = "LIBRO_IVA_DIGITAL{}.{}"

        sale_file = self.sale_presentation.generate(self.invoices)
        sale_file.file_name = base_name.format("_VENTAS_CBTE", "txt")

        sale_vat_file = self.sale_iva_presentation.generate(self.invoices)
        sale_vat_file.file_name = base_name.format("_VENTAS_ALICUOTAS", "txt")

        purchase_file = self.purchase_presentation.generate(self.invoices)
        purchase_file.file_name = base_name.format("_COMPRAS_CBTE", "txt")

        purchase_vat_file = self.purchase_iva_presentation.generate(self.invoices)
        purchase_vat_file.file_name = base_name.format("_COMPRAS_ALICUOTAS", "txt")

        purchase_imports_file = self.purchase_import_presentation.generate(self.invoices)
        purchase_imports_file.file_name = base_name.format("_IMPORTACION_BIENES_ALICUOTA", "txt")

        purchase_imports_invoice_file = self.purchase_import_invoice_presentation.generate(self.invoices)
        purchase_imports_invoice_file.file_name = base_name.format("_IMPORTACION_BIENES_CBTE", "txt")

        fiscal_credit_service_import_file = self.generate_fiscal_vat_digital_book_credit_service_import_file()
        fiscal_credit_service_import_file.file_name = base_name.format("_IMPORTACION_SERVICIOS_CREDITO_FISCAL", "txt")

        # Se genera el archivo zip que contendra los archivos
        reginfo_zip_file = self.generate_reginfo_zip_file(
            [
                sale_file,
                sale_vat_file,
                purchase_file,
                purchase_vat_file,
                purchase_imports_file,
                purchase_imports_invoice_file,
                fiscal_credit_service_import_file
            ]
        )
        # Se escriben en la presentacion los datos generados
        self.write({
            'generation_time': datetime.now(),
            'sale_filename': sale_file.file_name,
            'sale_file': sale_file.get_encoded_string(),
            'sale_vat_filename': sale_vat_file.file_name,
            'sale_vat_file': sale_vat_file.get_encoded_string(),
            'purchase_filename': purchase_file.file_name,
            'purchase_file': purchase_file.get_encoded_string(),
            'purchase_vat_filename': purchase_vat_file.file_name,
            'purchase_vat_file': purchase_vat_file.get_encoded_string(),
            'purchase_imports_filename': purchase_imports_file.file_name,
            'purchase_imports_file': purchase_imports_file.get_encoded_string(),
            'purchase_imports_invoice_filename': purchase_imports_invoice_file.file_name,
            'purchase_imports_invoice_file': purchase_imports_invoice_file.get_encoded_string(),
            'fiscal_credit_service_import_filename': fiscal_credit_service_import_file.file_name,
            'fiscal_credit_service_import_file': fiscal_credit_service_import_file.get_encoded_string(),
            'reginfo_zip_filename': base_name.format("", "zip"),
            'reginfo_zip_file': reginfo_zip_file,
        })

    name = fields.Char(
        string="Nombre",
        required=True,
    )
    generation_time = fields.Datetime(
        string="Fecha y hora de generacion",
    )
    date_from = fields.Date(
        string="Desde",
        required=True,
    )
    date_to = fields.Date(
        string="Hasta",
        required=True,
    )
    sequence = fields.Char(
        string="Secuencia",
        size=2,
        required=True,
        default='00',
    )
    with_prorate = fields.Boolean(
        string="Con prorrateo",
    )
    sale_file = fields.Binary(
        string="Ventas",
        filename="sale_filename",
    )
    sale_filename = fields.Char(
        string="Nombre de archivo de ventas",
    )
    sale_vat_file = fields.Binary(
        string="Ventas alicuotas",
        filename="sale_vat_filename",
    )
    sale_vat_filename = fields.Char(
        string="Nombre de archivo de ventas alicuotas",
    )
    purchase_file = fields.Binary(
        string="Compras",
        filename="purchase_filename",
    )
    purchase_filename = fields.Char(
        string="Nombre de archivo de compras",
    )
    purchase_vat_file = fields.Binary(
        string="Compras alicuotas",
        filename="purchase_vat_filename",
    )
    purchase_vat_filename = fields.Char(
        string="Nombre de archivo de compras alicuotas",
    )
    purchase_imports_file = fields.Binary(
        string="Compras importaciones alícuotas",
        filename="purchase_imports_filename",
    )
    purchase_imports_filename = fields.Char(
        string="Nombre de archivo de compras importaciones alícuotas",
    )
    purchase_imports_invoice_file = fields.Binary(
        string="Compras importaciones",
        filename="purchase_imports_vat_filename",
    )
    purchase_imports_invoice_filename = fields.Char(
        string="Nombre de archivo de compras importaciones",
    )
    fiscal_credit_service_import_file = fields.Binary(
        string="Credito fiscal de importacion de servicios",
        filename="fiscal_credit_service_import_filename",
    )
    fiscal_credit_service_import_filename = fields.Char(
        string="Nombre de archivo de credito fiscal de importacion de servicios",
    )
    reginfo_zip_file = fields.Binary(
        string="ZIP de regimen de informacion",
        filename="reginfo_zip_filename",
    )
    reginfo_zip_filename = fields.Char(
        string="Nombre de archivo ZIP de regimen de informacion",
    )
    company_id = fields.Many2one(
        string="Compania",
        comodel_name="res.company",
        required=True,
        default=lambda self: self.env.company,
    )

    @staticmethod
    def generate_fiscal_vat_digital_book_credit_service_import_file():
        """
        Esta presentacion no se utiliza actualmente
        """
        raise NotImplementedError

    def get_instance_presentation(self, class_name, data, builder, with_prorate=False):
        class_mapping = self.get_class_mapping_dict()
        if with_prorate:
            return class_mapping[class_name](data=data, builder=builder, with_prorate=with_prorate)
        return class_mapping[class_name](data=data, builder=builder)

    def get_class_mapping_dict(self):
        return {
            'purchase_presentation': PurchaseInvoicePresentation,
            'purchase_iva_presentation': PurchaseIvaPresentation,
            'purchase_import_presentation': PurchaseImportationPresentation,
            'purchase_import_invoice_presentation': PurchaseImportationInvoicePresentation,
            'sale_presentation': SaleInvoicePresentation,
            'sale_iva_presentation': SaleVatInvoicePresentation
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
