# -*- encoding: utf-8 -*-

import io, base64, xlwt, csv
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime


class VatDiary(models.Model):
    _name = 'vat.diary'
    _description = 'Subdiario de IVA'

    type = fields.Selection([
        ('sales', 'Ventas'),
        ('purchases', 'Compras')
    ], 'Tipo', required=True)
    include_suffered_retentions = fields.Boolean(string="Incluir retenciones sufridas")
    separate_not_taxable_from_exempt = fields.Boolean(string="Separar No Gravado y Exento")
    date_from = fields.Date('Desde', required=True)
    date_to = fields.Date('Hasta', required=True)
    report = fields.Binary('Reporte XLS', readonly=True)
    report_filename = fields.Char(string='Nombre archivo')
    csv_report = fields.Binary('Reporte CSV', readonly=True)
    csv_report_filename = fields.Char(string='Nombre archivo CSV')
    company_id = fields.Many2one('res.company', string="Compañía", default=lambda l: l.env.company)

    @api.depends('type', 'date_from', 'date_to')
    def _compute_display_name(self):
        for r in self:
            name = ["Subdiario IVA"]
            if r.type:
                name.append(f" {dict(r._fields['type'].selection).get(r.type)}")
            if r.date_from and r.date_to:
                name.append(f": {r.date_from.strftime('%d/%m/%Y')} - {r.date_to.strftime('%d/%m/%Y')}")
            r.display_name = ''.join(name)

    @api.onchange('type')
    def onchange_type(self):
        self.include_suffered_retentions = False

    @api.constrains('date_from', 'date_to')
    def validate_date_range(self):
        if any(r.date_from > r.date_to for r in self):
            raise ValidationError("Rango inválido de fechas")

    def _get_retentions_search_domain(self):
        return [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('payment_id.state', 'not in', ('draft', 'cancel')),
            ('payment_id.payment_type', '=', 'inbound'),
            ('company_id', '=', self.env.company.id)
        ]

    def _get_retentions(self):
        return self.env['account.payment.retention'].search(self._get_retentions_search_domain())

    def _get_invoices_search_domain(self):
        return [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('state', 'not in', ('draft', 'cancel')),
            ('company_id', '=', self.env.company.id),
            ('voucher_type_id', '!=', False),
            ('fiscal_position_id.show_vat_diary', '=', True),
            ('move_type', 'in', ('out_invoice', 'out_refund') if self.type == 'sales' else ('in_invoice', 'in_refund'))
        ]

    def _get_invoices(self):
        invoices = self.env['account.move'].search(self._get_invoices_search_domain())
        invoices._check_vat_diary_voucher_name()
        return invoices

    def _get_vouchers_data(self, vouchers):
        # Se genera una lista de diccionarios con todos los documentos a incluir en el reporte
        return [voucher.get_vat_diary_dict() for voucher in vouchers]

    def _get_taxes_position(self, invoices, retentions=None):
        """
        Devuelve los impuestos de las facturas en un diccionario con un valor distinto para cada uno
        :param invoices: account.invoice - Del cual se obtendran todos los impuestos
        :param retentions: account.payment.retention o None - Del cual se obtendran los impuestos de retenciones
        :return dict: de la forma {account.tax(): posicion}
        """
        res = {}
        position = 0

        taxes = invoices.mapped('line_ids').filtered(
            lambda l: abs(l.amount_currency or l.balance) or (l.tax_line_id.is_vat and not l.tax_line_id.is_exempt)
        ).mapped('tax_line_id')

        if retentions:
            taxes |= retentions.mapped('retention_id').get_taxes(self.env.company)

        # Ordenamos los impuestos para tener el IVA primero y removemos duplicados
        sorted_taxes = taxes.sorted(key=lambda x: (not x.is_vat, x.vat_diary_sequence, x.name))

        # Bases de IVA
        for tax in sorted_taxes.filtered(lambda l: l.is_vat):
            res[tax] = position
            position += 1

        # No gravado y exento
        position += 2 if self.separate_not_taxable_from_exempt else 1

        # Importes de IVA
        position += len(sorted_taxes.filtered(lambda l: l.is_vat))

        # Otros impuestos
        for tax in sorted_taxes.filtered(lambda l: not l.is_vat):
            res[tax] = position
            position += 1

        return res

    def get_vat_tax_count(self, taxes_position):
        return sum(t.is_vat for t in taxes_position.keys())

    def get_last_position(self, taxes_position):
        # Obtenemos el ultimo impuesto para saber en que columna van los totales
        if taxes_position:
            last_tax = max(taxes_position, key=taxes_position.get)
            # Los totales van a estar una columna después de la del último impuesto
            last_position = taxes_position[last_tax] + 1
            # Si todos los impuestos son IVA, le sumo 1 o 2 a la posición para contemplar las columnas de no gravado y
            # exento; además sumo la cantidad de impuestos que se van a mostrar en el subdiario, para reflejar que hay
            # dos columnas para cada IVA (base e importe)
            # En caso de que haya percepciones o retenciones no hace falta correr la posición porque vienen
            # después de todas las demás columnas
            if all(t.is_vat for t in taxes_position.keys()):
                last_position += 2 if self.separate_not_taxable_from_exempt else 1
                last_position += len(taxes_position)
        else:
            last_position = 2 if self.separate_not_taxable_from_exempt else 1
        return last_position

    def _get_header(self):
        """ Genero un diccionario con los valores basicos de la cabecera del reporte """
        return {
            0: 'Fecha',
            1: 'Razón social',
            2: 'N° documento',
            3: 'Condición IVA',
            4: 'Tipo',
            5: 'Comprobante',
            6: 'Jurisdicción',
            7: 'Concepto',
        }

    def get_header_values(self, taxes_position):
        """
        Crea la estructura de datos para la cabecera del reporte
        :param taxes_position: diccionario que contiene la posicion del impuesto y el impuesto
        :return header: diccionario con la posicion y valor, ej: {0: 'Fecha', 1: 'Razon Social'..}
        """
        header = self._get_header()
        for tax in taxes_position:
            if tax.is_vat:
                header[len(header)] = (tax.description or tax.name) + ' - Base'

        if self.separate_not_taxable_from_exempt:
            header[len(header)] = 'No Gravado'
            header[len(header)] = 'Exento'
        else:
            header[len(header)] = 'No Gravado/Exento'

        for tax in taxes_position:
            if tax.is_vat:
                header[len(header)] = (tax.description or tax.name) + ' - Importe'

        for tax in taxes_position:
            if not tax.is_vat:
                header[len(header)] = tax.description or tax.name

        header[len(header)] = 'Total'

        return header

    def _get_voucher_values(self, voucher, last_position, size):
        """ Seteo los valores para cada posicion de una fila"""
        vals = {
            0: voucher.get('date'),
            1: voucher.get('partner'),
            2: voucher.get('vat'),
            3: voucher.get('fiscal_position'),
            4: voucher.get('voucher_type'),
            5: voucher.get('voucher'),
            6: voucher.get('jurisdiction'),
            7: voucher.get('concept', ''),
        }
        vals[last_position + size] = voucher.get('total')
        return vals

    def get_voucher_details(self, taxes_position, vouchers, size_header, last_position):
        """
        Crea la estructura de datos para los detalle del reporte, los cuales son datos de invoices,
        o de retenciones si estas fueran informadas.
        :param taxes_position: diccionario que contiene la posicion del impuesto y el impuesto
        :param vouchers: Lista de account.move y/o account.payment.retention - De donde se tomaran los datos
        :size_header: int - Tamaño del encabezado
        :last_position: int - Indice de la última posición de las columnas
        :return: lista de diccionarios, cada uno con la posicion y valor, ej: {0: '01/01/2000'}
        """
        res = []
        for voucher in vouchers:
            values = self._get_voucher_values(voucher, last_position, size_header)
            record = self.env[voucher.get('model')].browse(voucher.get('id'))
            record.with_context(
                separate_not_taxable_from_exempt=self.separate_not_taxable_from_exempt).update_vat_diary_values(
                taxes_position, values, size_header)
            res.append(values)
        return res

    def get_details_values(self, taxes_position, invoices, retentions=None):
        """
        Crea la estructura de datos para los detalle del reporte, los cuales son datos de invoices,
        o de retenciones si estas fueran informadas.
        :param taxes_position: diccionario que contiene la posicion del impuesto y el impuesto
        :param invoices: account.move - De donde se tomaran los datos
        :param retentions: account.payment.retention o None - De donde se tomaran los datos
        :return: lista de diccionarios, cada uno con la posicion y valor, ej: {0: '01/01/2000'}
        """
        last_position = self.get_last_position(taxes_position)
        size_header = len(self._get_header())
        vouchers = list(invoices)
        if retentions:
            vouchers.extend(list(retentions))
        return self.get_voucher_details(taxes_position, self._get_vouchers_data(vouchers), size_header, last_position)

    def sort_detail_values(self, detail_values):
        # Ordeno por fecha, tipo y nombre según las claves de los dict
        # devueltos por _get_details_values
        return sorted(detail_values, key=lambda x: (datetime.strptime(x.get(0), '%d/%m/%Y'), x.get(4), x.get(5)))

    def get_report_values(self):
        """
        Devuelve los datos de cabecera y detalles del reporte a armar de las invoices obtenidas
        :return list: Lista de diccionarios con la cabecera y detalles
            [{0: 'Fecha',...}{0: '01/01/2000,...}]
        """
        invoices = self._get_invoices()
        if self.include_suffered_retentions:
            retentions = self._get_retentions()
            if not (invoices or retentions):
                raise ValidationError("No se han encontrado documentos para ese rango de fechas")
            invoices.validate_voucher_name()
            taxes_position = self._get_taxes_position(invoices, retentions)
            header = self.get_header_values(taxes_position)
            details = self.get_details_values(taxes_position, invoices, retentions)
            details = self.sort_detail_values(details)
        else:
            if not invoices:
                raise ValidationError("No se han encontrado documentos para ese rango de fechas")
            invoices.validate_voucher_name()
            taxes_position = self._get_taxes_position(invoices)
            header = self.get_header_values(taxes_position)
            details = self.get_details_values(taxes_position, invoices)
            details = self.sort_detail_values(details)

        return [header] + details

    def generate_xls_report(self):
        """ Crea un xls con los valores obtenidos de get_report_values"""
        values = self.get_report_values()

        # Preparamos el workbook y la hoja
        wbk = xlwt.Workbook()
        style = xlwt.easyxf(
            'font: bold on,height 240,color_index 0X36;'
            'align: horiz center;'
            'borders: left thin, right thin, top thin'
        )
        diary_type = self.display_name.split(':')[0]
        sheet = wbk.add_sheet(diary_type)
        # Ancho de las columnas
        sheet.col(0).width = 2500
        sheet.col(1).width = 6000
        sheet.col(2).width = 4000
        sheet.col(3).width = 6000
        sheet.col(4).width = 5000
        sheet.col(5).width = 5000
        sheet.col(6).width = 4000

        row_number = 0
        total_cols = 0
        # Header
        for col in values[0]:
            # Le asignamos el ancho a las columnas de importes
            if total_cols > 7:
                sheet.col(col).width = 3500
            sheet.write(row_number, col, values[0][col], style)
            total_cols += 1

        # Detalles
        row_number += 1
        for value in values[1:]:
            for col in value:
                sheet.write(row_number, col, value[col])
            row_number += 1
        header = self._get_header()
        size_header = len(header)
        for x in range(size_header, total_cols):
            column_start = xlwt.Utils.rowcol_to_cell(1, x)
            column_end = xlwt.Utils.rowcol_to_cell(row_number - 1, x)
            sheet.write(row_number, x, xlwt.Formula('SUM(' + column_start + ':' + column_end + ')'))

        # Exportamos y guardamos
        file_data = io.BytesIO()
        wbk.save(file_data)
        out = base64.encodebytes(file_data.getvalue())
        self.report = out

        date_from = self.date_from.strftime('%d-%m-%Y')
        date_to = self.date_to.strftime('%d-%m-%Y')
        self.report_filename = diary_type + " " + date_from + ' a ' + date_to + '.xls'

    def sort_voucher_values(self, voucher_values):
        # Ordeno por fecha, tipo y numero de vat según las claves de los dict
        # devueltos por _get_pdf_values
        return sorted(voucher_values, key=lambda x: (
            datetime.strptime(x.get('date'), '%d/%m/%Y'), x.get('voucher_type'), x.get('name')
        ))

    def get_pdf_values(self):
        invoices = list(self._get_invoices())
        retentions = []
        if self.include_suffered_retentions:
            retentions = list(self._get_retentions())
        vouchers = invoices + retentions
        if not vouchers:
            raise ValidationError("No se han encontrado documentos para ese rango de fechas")
        voucher = self._get_vouchers_data(vouchers)
        return self.sort_voucher_values(voucher)

    def get_csv_details_values(self, invoices):
        values = []
        for i in invoices:
            values.extend(getattr(i, f'get_csv_{self.type}_vat_diary_list')())
        return values

    def get_csv_report_values(self):
        invoices = self._get_invoices()
        if not invoices:
            raise ValidationError("No se han encontrado documentos para ese rango de fechas")
        return self.get_csv_details_values(invoices)

    def generate_csv_report(self):
        file_data = io.StringIO()
        writer = csv.writer(file_data, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        for row in self.get_csv_report_values():
            writer.writerow(row)
        self.csv_report = base64.encodebytes(file_data.getvalue().encode('ascii'))
        
        diary_type = self.display_name.split(':')[0]
        date_from = self.date_from.strftime('%d-%m-%Y')
        date_to = self.date_to.strftime('%d-%m-%Y')
        self.csv_report_filename = diary_type + " " + date_from + ' a ' + date_to + '.csv'

    def get_iva_totals(self, iva, dictionary={}):
        # En caso de proporcionar dictionary actualiza el diccionario con los valores que correspondan
        # del diccionario de los impuestos pasados en iva.
        # En caso de no pasar dictionary genera y devuelve un diccionario de diccionarios,
        # con el formato {id_impuesto: {'name': 'IVA 21%','base': 100.0, 'amount': 21.0}}, sumando los totales por impuesto
        # Agrego los impuestos IVA
        for key, dic in iva.items():
            if dictionary.get(key):
                dictionary[key]['amount'] += dic.get('amount', 0.0)
                dictionary[key]['base'] += dic.get('base', 0.0)
            else:
                dictionary[key] = dic.copy()
        return dictionary

    def get_not_iva_perception_totals(self, not_iva_perception, dictionary={}):
        # En caso de proporcionar dictionary actualiza el diccionario con los valores que correspondan
        # del diccionario de los impuestos pasados en not_iva_perception.
        # En caso de no pasar dictionary genera y devuelve un diccionario de diccionarios,
        # con el formato {id_impuesto: {'name': 'Impuesto interno','base': 100.0, 'amount': 21.0}}, sumando los totales por impuesto
        # Agrego los impuestos que no son IVA ni percepcioens
        for key, dic in not_iva_perception.items():
            if dictionary.get(key):
                dictionary[key]['amount'] += dic.get('amount', 0.0)
                dictionary[key]['base'] += dic.get('base', 0.0)
            else:
                dictionary[key] = dic.copy()
        return dictionary

    def get_no_taxable_total(self, no_taxable, dictionary={}):
        # En caso de proporcionar dictionary actualiza el diccionario con los valores que correspondan
        # del diccionario de los impuestos no gravados pasados en no_taxable .
        # En caso de no pasar dictionary genera y devuelve un diccionario de diccionarios,
        # con el formato {id_impuesto: {'name': 'No gravado', 'amount': 20.0}}, solo en caso de que el importe no_taxable sea diferente de 0.0
        # Agrego el monto No gravado
        if dictionary.get('not_taxable'):
            dictionary['not_taxable']['amount'] += no_taxable
        elif no_taxable:
            dictionary['not_taxable'] = {'name': 'No gravado', 'amount': no_taxable}
        return dictionary

    def get_exempt_total(self, exempt, dictionary={}):
        # En caso de proporcionar dictionary actualiza el diccionario con los valores que correspondan
        # del diccionario de los impuestos no gravados pasados en exempt .
        # En caso de no pasar dictionary genera y devuelve un diccionario de diccionarios,
        # con el formato {id_impuesto: {'name': 'exento', 'amount': 20.0}}, solo en caso de que el importe exempt sea diferente de 0.0
        # Agrego el monto No gravado
        # Agrego el monto exento
        if dictionary.get('exempt'):
            dictionary['exempt']['amount'] += exempt
        elif exempt:
            dictionary['exempt'] = {'name': 'Exento', 'amount': exempt}
        return dictionary

    def get_fiscal_debit_total(self, moves):
        # Devuelve un diccionario de diccionarios, con el formato {id_impuesto: {'name': 'IVA 21%', 'amount': 21.0}}
        # Filtro las lineas del reporte, por las lineas correspondientes al debito fiscal que son
        # las facturas de proveedor y las facturas rectificativas (NC) de cliente
        debit = {}
        for line in filter(lambda l: l.get('type') in ['in_refund', 'out_invoice'], moves):
            # Agrego los totales por impuesto al diccionario y los voy actualizadondo segun corresponda,en cada iteracion
            debit = self.get_iva_totals(line.get('iva', {}), debit)

            # Agrego los totales por impuesto interno al diccionario y los voy actualizadondo segun corresponda,en cada iteracion
            debit = self.get_not_iva_perception_totals(line.get('not_iva_perception', {}), debit)

            # Agrego el monto no gravado y lo voy actualizadondo segun corresponda,en cada iteracion
            debit = self.get_no_taxable_total(line.get('not_taxable', 0.0), debit)

            # Agrego el monto exento y lo voy actualizadondo segun corresponda,en cada iteracion
            debit = self.get_exempt_total(line.get('exempt', 0.0), debit)
        return debit

    def get_fiscal_credit_total(self, moves):
        # Filtro las lineas del reporte, por las lineas correspondientes al credito fiscal que son
        # las facturas de clientes y las facturas rectificativas (NC) de proveedores
        credit = {}
        for line in filter(lambda l: l.get('type') in ['out_refund', 'in_invoice'], moves):
            # Agrego los totales por impuesto al diccionario
            credit = self.get_iva_totals(line.get('iva', {}), credit)

            # Agrego los totales po impuesto interno al diccionario
            credit = self.get_not_iva_perception_totals(line.get('not_iva_perception', {}), credit)

            # Agrego el monto no gravado y lo voy actualizadondo segun corresponda,en cada iteracion
            credit = self.get_no_taxable_total(line.get('not_taxable', 0.0), credit)

            # Agrego el monto exento y lo voy actualizadondo segun corresponda,en cada iteracion
            credit = self.get_exempt_total(line.get('exempt', 0.0), credit)
        return credit

    def get_special_regimes_total(self, moves):
        reg = {}
        # Itero todas las lineas del reporte
        for line in moves:
            # Si la linea es de retencion la agrego tomando el total de la linea
            if line.get('type') == 'retention':
                if reg.get(line.get('retention_id')):
                    reg[line.get('retention_id')]['amount'] += line.get('total', 0.0)
                else:
                    reg[line.get('retention_id')] = {'name': line.get('retention'), 'amount': line.get('total', 0.0)}
            else:
                # Si la linea no es de retencion, entonces tengo que iterar las percepciones de la linea
                # e ir agregandolas o actulizando el diccionario
                perceptions = line.get('perceptions', {})
                for key, dic in perceptions.items():
                    if reg.get(key):
                        reg[key]['amount'] += dic.get('amount', 0.0)
                    else:
                        reg[key] = dic.copy()
        return reg

    def generate_pdf_report(self):
        moves = self.get_pdf_values()
        data = {
            'diary_id': self.id,
            'moves': moves,
            'debits': self.get_fiscal_debit_total(moves),
            'credits':  self.get_fiscal_credit_total(moves),
            'special_regimes': self.get_special_regimes_total(moves)
        }
        return self.env.ref('l10n_ar_vat_diary.pdf_iva_diary_report_action').report_action(self, data=data)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
