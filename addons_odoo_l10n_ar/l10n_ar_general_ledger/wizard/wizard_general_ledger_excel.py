# -*- coding: utf-8 -*-

import io
import base64
from collections import OrderedDict

import xlwt as xlwt
from odoo import models, fields, api
from odoo.exceptions import ValidationError

COLS = {
    'fecha': 0,
    'cod_cuenta': 1,
    'nom_cuenta': 2,
    'debe': 3,
    'haber': 4,
    'ref': 5,
    'partner': 6,
}


class WizardGeneralLedgerExcel(models.TransientModel):
    _name = 'wizard.general.ledger.excel'
    _description = 'Wizard de libro mayor en excel'

    date_from = fields.Date(
        string="Desde",
        default=fields.Date.today(),
        required=True,
    )

    date_to = fields.Date(
        string="Hasta",
        default=fields.Date.today(),
        required=True,
    )

    ledger = fields.Binary(
        string="Mayor"
    )

    @api.constrains('date_from', 'date_to')
    def check_dates(self):
        if self.date_from > self.date_to:
            raise ValidationError("La fecha desde no puede ser mayor a la fecha hasta.")

    @staticmethod
    def get_values(moves):
        """
        Genera una lista con datos (fecha, codigo de cuenta, nombre de cuenta, debe, haber, nombre de asiento y
        nombre de partner) de cada linea de asiento y se la asigna al asiento en un diccionario
        :param moves: recordset de asientos sobre los cuales se generaran los datos
        :return: diccionario con lineas por cada asiento
        """
        lines_by_move = OrderedDict()
        line_ids = moves.mapped('line_ids').filtered(lambda aml: aml.display_type not in ('line_section', 'line_note')).sorted(lambda l: (l.move_id.date, l.full_voucher_name, l.move_id.id))
        for line in line_ids:
            account = line.account_id
            if not lines_by_move.get(line.full_voucher_name):
                lines_by_move[line.full_voucher_name] = []
            lines_by_move[line.full_voucher_name].append((line.date.strftime('%d/%m/%Y'),
                                                     account.code.replace('.', ''),
                                                     account.name,
                                                     line.debit or '-',
                                                     line.credit or '-',
                                                     line.name or '',
                                                     line.partner_id.name if line.partner_id else ''))
        return lines_by_move

    def fill_sheet(self, sheet, values):
        """
        Rellena una hoja de calculo con los valores suministrados (con formato similar al devuelto por get_values)
        :param sheet: la hoja a rellenar
        :param values: diccionario de valores (la key es un asiento y el value, una lista de tuplas)
        """
        style_regular = xlwt.easyxf('align: horiz left;')
        style_title = xlwt.easyxf('align: horiz left; font: bold on;')
        current_row = 0
        sheet.write(current_row, 0, "ASIENTO", style_title)
        sheet.write(current_row, 1, "FECHA", style_title)
        sheet.write(current_row, 2, "COD. CUENTA", style_title)
        sheet.write(current_row, 3, "CUENTA", style_title)
        sheet.write(current_row, 5, "DEBE", style_title)
        sheet.write(current_row, 7, "HABER", style_title)
        sheet.write(current_row, 8, "APUNTE", style_title)
        sheet.write(current_row, 9, "PARTNER", style_title)
        current_row += 1
        symbol = self.env.user.company_id.currency_id.symbol
        for move, lines in values.items():
            for line in lines:
                sheet.write(current_row, 1, line[COLS.get('fecha')], style_regular)
                sheet.write(current_row, 2, line[COLS.get('cod_cuenta')], style_regular)
                sheet.write(current_row, 3, line[COLS.get('nom_cuenta')], style_regular)
                sheet.write(current_row, 4, symbol, style_regular)
                sheet.write(current_row, 5, line[COLS.get('debe')], style_regular)
                sheet.write(current_row, 6, symbol, style_regular)
                sheet.write(current_row, 7, line[COLS.get('haber')], style_regular)
                sheet.write(current_row, 8, line[COLS.get('ref')], style_regular)
                sheet.write(current_row, 9, line[COLS.get('partner')], style_regular)
                current_row += 1

            for x in [5, 7]:
                column_start = xlwt.Utils.rowcol_to_cell(current_row - len(lines), x)
                column_end = xlwt.Utils.rowcol_to_cell(current_row - 1, x)
                sheet.write(current_row, x-1, symbol, style_title)
                sheet.write(current_row, x, xlwt.Formula('SUM(' + column_start + ':' + column_end + ')'), style_title)
            sheet.write(current_row, 0, move, style_title)
            current_row += 1

    def domain_account_move_search(self):
        return [('date', '>=', self.date_from), ('date', '<=', self.date_to), ('state', '=', 'posted')]

    def generate_ledger(self):
        """
        Genera y descarga el libro mayor en formato xls
        :return: la descarga del archivo
        """
        moves = self.env['account.move'].search(self.domain_account_move_search())
        values = self.get_values(moves)
        wb = xlwt.Workbook()
        sheet = wb.add_sheet("Diario")
        self.fill_sheet(sheet, values)

        file_data = io.BytesIO()
        wb.save(file_data)
        file = base64.b64encode(file_data.getvalue())
        self.ledger = file

        date_from = fields.Date.from_string(self.date_from).strftime('%d-%m-%Y')
        date_to = fields.Date.from_string(self.date_to).strftime('%d-%m-%Y')
        filename = 'Libro diario ' + date_from + ' - ' + date_to

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_general_ledger?wizard_id=%s&filename=%s' % (self.id, filename + '.xls'),
            'target': 'new',
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
