# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import base64
import tempfile
import datetime


class BankAutomaticReconcileWizard(models.TransientModel):

    _name = 'bank.automatic.reconcile.wizard'

    COLS = {
        'date': 0,
        'name': 1,
        'debit': 2,
        'credit': 3,
    }

    file = fields.Binary(
        string='Extracto',
        filename="filename",
        help="El archivo debera ser un XLSX con 4 columnas: Fecha, Descripcion, Debito, Credito."
    )
    filename = fields.Char(string='Nombre Archivo')
    date_from = fields.Date('Fecha desde')
    date_to = fields.Date('Fecha Hasta')
    bank_line_ids = fields.One2many(
        'bank.automatic.reconcile.bank.line',
        'bank_automatic_reconcile_id',
        string='Movimientos'
    )
    found_line_ids = fields.One2many(
        'bank.automatic.reconcile.found.line',
        'bank_automatic_reconcile_id',
        string='Movimientos encontrados'
    )
    not_found_line_ids = fields.One2many(
        'bank.automatic.reconcile.not.found.line',
        'bank_automatic_reconcile_id',
        string='Movimientos no encontrados'
    )

    def concile_movements(self):
        if not (self.date_to and self.date_from):
            raise ValidationError("Debe definir las fechas para poder conciliar.")
        return self.env['bank.reconcile.wizard'].create({
            'date_start': self.date_from,
            'date_stop': self.date_to,
        }).with_context(active_ids=self.found_line_ids.mapped('move_line_id.id')).create_conciliation()

    def load_file(self):
        book = self.open_excel_book()
        self.bank_line_ids = None
        self.create_bank_lines(book)
        move_lines = self.find_move_lines()
        move_lines_found = []
        bank_lines_found = self.env['bank.automatic.reconcile.bank.line']

        for bank_line in self.bank_line_ids:
            move_line = move_lines.filtered(
                lambda x: x.debit and x.debit == bank_line.debit or x.credit and x.credit == bank_line.credit
            )
            if move_line:
                move_lines -= move_line[0]
                move_lines_found.append((move_line[0], bank_line.name))
                bank_lines_found += bank_line

        for line in move_lines_found:
            self.found_line_ids |= self.found_line_ids.new({'move_line_id': line[0], 'bank_description': line[1]})
        for line in move_lines:
            self.not_found_line_ids |= self.not_found_line_ids.new({'move_line_id': line})

        self.bank_line_ids -= bank_lines_found

    @api.onchange('file', 'date_from', 'date_to')
    def onchange_file(self):
        if self.file:
            self.load_file()

    def find_move_lines(self):
        reconcile = self.env['account.bank.reconcile'].browse(self.env.context.get('active_id'))
        domain = [
            ('bank_reconciled', '=', False),
            ('account_id', '=', reconcile.account_id.id),
            ('move_id.state', '=', 'posted')
        ]
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValidationError("La fecha desde no puede ser mayor que la fecha hasta.")

        if self.date_from:
            domain.append(('date', '>=', self.date_from))
        if self.date_to:
            domain.append(('date', '<=', self.date_to))

        return self.env['account.move.line'].search(domain)

    def create_bank_lines(self, book):
        error_rows = []
        r = 2
        import xlrd
        for row in self.sheet_to_array(book.sheet_by_index(0)):
            try:
                date_tuple = xlrd.xldate_as_tuple(row[self.COLS['date']], book.datemode)
                date = datetime.datetime(*date_tuple[0:6]).date()
                name = str(row[self.COLS['name']])
                debit = float(row[self.COLS['debit']])
                credit = float(row[self.COLS['credit']])
                if date and name and (debit or credit):
                    if not error_rows:
                        self.bank_line_ids |= self.bank_line_ids.new({
                            'name': name,
                            'date': date,
                            'debit': debit,
                            'credit': credit,
                        })
                else:
                    error_rows.append(r)
            except Exception as e:
                error_rows.append(e)
            r += 1

        if error_rows:
            error_rows_str = str(error_rows)[1:-1]  # para no mostrar los corchetes
            raise ValidationError("ERROR! los siguientes numeros de fila no poseen datos validos: \n{}".format(error_rows_str))

    def open_excel_book(self):
        """
        Guarda el archivo especificado en el campo en una carpeta temporal y lo abre.
        :return: la primer hoja del archivo de Excel subido, abierta.
        """
        if self.filename.split(".")[-1].lower() != "xlsx":
            raise ValidationError('Error\nDebe utilizar un archivo xlsx (Excel 2007 o superior).')
        try:
            import xlrd
        except:
            raise ValidationError('Error\nEl modulo xlrd no esta instalado.')
        try:
            temp = tempfile.NamedTemporaryFile()
            temp.write(base64.b64decode(self.file))
            temp.seek(0)
        except:
            raise ValidationError('Error\nEl archivo elegido no es valido.')
        try:
            return xlrd.open_workbook(temp.name)
        except:
            raise ValidationError('Error\nEl archivo elegido no es valido.')

    def sheet_to_array(self, sheet):
        """
        Lee todos los datos de una hoja de Excel.
        :param sheet: la hoja a leer
        :return: un array con todas las filas y columnas.
        """
        values = []
        for r in range(sheet.nrows - 1):
            row = []
            for c in range(sheet.ncols):
                col = sheet.cell(r + 1, c).value
                # Si el dato leido es un float con decimal .0, lo convierte a int
                try:
                    if col.is_integer():
                        col = int(col)
                except:
                    pass
                row.append(col)
            values.append(row)
        return values

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
