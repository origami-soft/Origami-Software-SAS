# -*- encoding: utf-8 -*-

from odoo import models
from odoo.exceptions import ValidationError
from datetime import datetime


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _get_report_action(self):
        return 'l10n_ar_stock_picking_report.action_selfprint_report' if self.cai else 'stock.action_report_delivery'

    def print_selfprint_or_standard_report(self):
        """ Si el remito tiene CAI se imprime el autoimpresor """
        self.ensure_one()
        ext_id = self._get_report_action()
        return self.env.ref(ext_id).report_action(self)

    def get_voucher_code(self):
        document_book = self.picking_type_id.get_document_book(self.company_id)
        return document_book.voucher_type_id.code if document_book else "R"

    def validate_selfprint_fields(self):
        # Se evita realizar las validaciones en caso de acceder desde studio
        if self.env.context.get('studio', False):
            return True

        company = self.company_id
        if not (company.start_date and company.iibb_number and company.street and company.city):
            raise ValidationError("Antes de imprimir, configurar la fecha de inicio de actividades"
                                  ", número de IIBB y dirección de la compañía")

        if self.state != 'done':
            raise ValidationError("No se puede imprimir un remito no realizado")

        if not self.cai:
            raise ValidationError("No se puede imprimir un remito sin CAI")

        return True
        
    def get_bar_code(self):
        self.ensure_one()
        code = str(int(self.get_voucher_code()))  # Para sacar el 0 del principio
        company = self.env.user.company_id
        company_vat = company.partner_id.vat
        
        picking_pos = self.name.split('-')[0]
        date = self.cai_due_date.strftime('%Y%m%d') if self.cai_due_date else False
        
        if company_vat and code and picking_pos and self.cai and date:
            cai_barcode = company_vat+code+picking_pos+self.cai+date
            verificator_code = self._get_verificator_code(cai_barcode)
            return cai_barcode+str(verificator_code)

    def _get_verificator_code(self, cai_barcode):
        try: barcode = int(cai_barcode)
        except ValueError: raise ValidationError('No se pudo generar el codigo de barras')
        barcode_numbers_list = list(map(int, str(barcode)))
        first = 0

        # Busco los numeros impares
        for odd in barcode_numbers_list[0::2]:
            first += odd
        second = first * 3
        third = 0

        # Busco los numeros pares
        for pair in barcode_numbers_list[1::2]:
            third += pair
        fourth = third+second
        
        return 10 - (fourth % 10) if fourth % 10 != 0 else 0
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
