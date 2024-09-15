# -*- encoding: utf-8 -*-

from collections import defaultdict
from odoo import models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def get_vat_diary_invoice_sign(self):
        # TODO: Mover responsabilidad a wizard.vat.diary
        return self.move_type in ['in_refund', 'out_refund'] and -1 or 1

    def _get_invoice_currency_rate(self):
        """ Calculo el rate de la factura """
        rate = 1
        currency_lines = self.line_ids.filtered(lambda x: x.amount_currency).sorted(
            lambda x: x.product_id, reverse=True
        )  # Las cuentas de ingresos/gastos
        if (self.company_id.currency_id != self.currency_id) and currency_lines:
            line_currency = currency_lines[0]
            rate = abs((line_currency.credit + line_currency.debit) / line_currency.amount_currency)
        return rate

    def update_vat_diary_values(self, taxes_position, vals, size_header):
        """Actualiza un diccionario con los datos de una fila del subdiario
        para las facturas

        :param taxes_position: Diccionario con las posiciones de los
        impuestos en el subdiario
        :type taxes_position: dict
        :param vals: Diccionario con los datos de una fila del subdiario
        :type vals: dict
        :param size_header: Tamaño del encabezado genérico del subdiario
        :type size_header: int
        """
        separate_not_taxable_from_exempt = self.env.context.get('separate_not_taxable_from_exempt')
        vat_tax_count = self.env['vat.diary'].get_vat_tax_count(taxes_position)
        iva_amounts = self.get_iva_amounts()

        for tax, value in iva_amounts.items():
            vals[taxes_position[self.env['account.tax'].browse(tax)] + size_header] = round(value.get('base'), 2)
        # Separo no gravado de exento si así lo requiriera el usuario
        if separate_not_taxable_from_exempt:
            vals[vat_tax_count + size_header] = self.get_not_taxable_amount()
            vals[vat_tax_count + size_header + 1] = self.get_exempt_amount()
        else:
            vals[vat_tax_count + size_header] = self.get_not_taxable_amount() + self.get_exempt_amount()
        for tax, value in iva_amounts.items():
            tax_obj = self.env['account.tax'].browse(tax)
            try:
                vals[taxes_position[tax_obj] + size_header + vat_tax_count + (2 if separate_not_taxable_from_exempt else 1)] = round(value.get('amount'), 2)
            except KeyError:
                if not tax_obj:
                    raise ValidationError("No se encontró impuesto para la percepción '{}' en la factura {}.".format(value.get('name', ''), self.full_voucher_name))
                raise ValidationError("Hay un problema con {} en la factura {}.".format(tax_obj.name, self.full_voucher_name))
        for tax, value in self.get_perception_amounts().items():
            tax_obj = self.env['account.tax'].browse(tax)
            try:
                vals[taxes_position[tax_obj] + size_header] = round(value.get('amount'), 2)
            except KeyError:
                if not tax_obj:
                    raise ValidationError("No se encontró impuesto para la percepción '{}' en la factura {}.".format(value.get('name', ''), self.full_voucher_name))
                raise ValidationError("Hay un problema con {} en la factura {}.".format(tax_obj.name, self.full_voucher_name))
        for tax, value in self.get_not_iva_perception_amounts().items():
            tax_obj = self.env['account.tax'].browse(tax)
            try:
                vals[taxes_position[tax_obj] + size_header] = round(value.get('amount'), 2)
            except KeyError:
                if not tax_obj:
                    raise ValidationError("No se encontró impuesto para la percepción '{}' en la factura {}.".format(value.get('name', ''), self.full_voucher_name))
                raise ValidationError("Hay un problema con {} en la factura {}.".format(tax_obj.name, self.full_voucher_name))

    def get_vat_diary_total(self):
        self.ensure_one()
        return abs(self.amount_total_signed) * self.get_vat_diary_invoice_sign()

    def get_iva_amounts(self):
        """ Devuelve un diccionario con todos los montos
        correspondientes al impuesto IVA de una factura

        :return: Montos de los impuestos IVA de la factura
        :rtype: dict
        """
        sign = self.get_vat_diary_invoice_sign()
        rate = self._get_invoice_currency_rate()
        # Se obtienen las lineas de apuntes contables de las facturas que corresponden a impuestos del tipo IVA
        iva_line = self.line_ids.filtered(lambda l: l.tax_line_id.is_vat and not l.tax_line_id.is_exempt)
        # Para los impuestos del tipo IVA se genera un diccionario de diccionarios
        # con el formato {'name': iva 21%, 'base': 100, 'amount': 21}
        iva = defaultdict(dict)
        for item in iva_line:
            base = sum(self.invoice_line_ids.filtered(lambda l: item.tax_line_id in l.tax_ids).mapped('price_subtotal'))
            amount = abs(item.amount_currency)
            if iva[item.tax_line_id.id]:
                iva[item.tax_line_id.id]['base'] += base * sign * rate
                iva[item.tax_line_id.id]['amount'] += amount * sign * rate
            else: 
                iva[item.tax_line_id.id] = {
                    'name': item.tax_line_id.name,
                    'base': base * sign * rate,
                    'amount': amount * sign * rate
                }
        return iva

    def get_not_iva_perception_amounts(self):
        """ Devuelve un diccionario con todos los montos
        correspondientes al impuesto no IVA ni Percepciones de una factura

        :return: Montos de los impuestos no IVA ni Percepciones de la factura
        :rtype: dict
        """
        sign = self.get_vat_diary_invoice_sign()
        rate = self._get_invoice_currency_rate()
        # Se obtienen las lineas de apuntes contables de las facturas que corresponden a impuestos internos
        no_iva_line = self.line_ids.filtered(lambda l: l.tax_line_id and l.tax_line_id.tax_group_id \
            in self.env['account.tax'].get_internal_tax_group(self.company_id))
        # Para los impuestos internos se genera un diccionario de diccionarios con el formato {'name': no iva ,'amount': 21}
        no_iva = defaultdict(dict)
        for item in no_iva_line:
            base = sum(self.invoice_line_ids.filtered(lambda l: item.tax_line_id in l.tax_ids).mapped('price_subtotal'))
            no_iva[item.tax_line_id.id] = {
                'name': item.tax_line_id.name,
                'base': base * sign * rate,
                'amount': item.price_subtotal * sign * rate
            }
        return no_iva

    def get_exempt_amount(self):
        """ Devuelve el monto exento de una factura

        :return: Monto exento de una factura
        :rtype: float
        """
        sign = self.get_vat_diary_invoice_sign()
        rate = self._get_invoice_currency_rate()
        return self.amount_exempt * sign * rate

    def get_not_taxable_amount(self):
        """ Devuelve el monto no gravado de una factura

        :return: Monto no gravado de una factura
        :rtype: float
        """
        sign = self.get_vat_diary_invoice_sign()
        rate = self._get_invoice_currency_rate()
        return self.amount_not_taxable * sign * rate

    def get_to_taxable_amount(self):
        """ Devuelve el monto neto gravado de una factura

        :return: Monto gravado de una factura
        :rtype: float
        """
        sign = self.get_vat_diary_invoice_sign()
        rate = self._get_invoice_currency_rate()
        return self.amount_to_tax * sign * rate

    def get_perception_amounts(self):
        """ Devuelve un diccionario con todos los montos
        correspondientes a las percepciones de una factura

        :return: Montos de las percepciones de la factura
        :rtype: dict
        """
        sign = self.get_vat_diary_invoice_sign()
        rate = self._get_invoice_currency_rate()
        # Para las percepciones que figuran en la grilla de percepciones
        # se genera un diccionario de tuplas con el formato {'tax_id(1,)': 10}
        perceptions = defaultdict(dict)
        for per in self.perception_ids:
            # Se toma el impuesto desde la percepcion
            perceptions[per.perception_id.get_taxes(self.company_id).id] = {
                'name': per.perception_id.name,
                'amount': per.amount * sign * rate
            }
        return perceptions

    def get_vat_diary_dict(self):
        """Devuelve los datos de una factura en un diccionario para el reporte de subdiario de IVA

        :return: Diccionario con datos de factura
        :rtype: dict
        """
        self.ensure_one()
        name_split = self.voucher_name.split('-')
        voucher_name = name_split[0].zfill(5) + '-' + name_split[1] if len(name_split) == 2 else self.voucher_name
        return {
            'id': self.id,
            'model': self._name,
            'type': self.move_type,
            'date': self.invoice_date.strftime('%d/%m/%Y') or self.date.strftime('%d/%m/%Y'),
            'partner': self.partner_id.name or '',
            'vat': self.partner_id.vat or '',
            'fiscal_position': self.fiscal_position_id.name or '',
            'voucher_type': self.voucher_type_id.prefix or (self.voucher_type_id.name or '')[:5],
            'voucher': voucher_name or '',
            'jurisdiction': self.jurisdiction_id.name or self.partner_id.state_id.name or '',
            'to_tax': self.get_to_taxable_amount(),
            'not_iva_perception': self.get_not_iva_perception_amounts(),
            'iva': self.get_iva_amounts(),
            'exempt': self.get_exempt_amount(),
            'not_taxable': self.get_not_taxable_amount(),
            'perceptions': self.get_perception_amounts(),
            'total': self.get_vat_diary_total(),
        }

    def validate_voucher_name(self):
        errors = []
        for r in self.filtered(lambda l: not l.voucher_name):
            if not r.invoice_date:
                errors.append("La {} realizada a {} no posee fecha.".format(
                    dict(r._fields['move_type']._description_selection(r.env)).get(r.move_type), r.partner_id.name)
                )
                continue
            errors.append("La {} realizada a {} el día {} no posee numeración correcta.".format(
               dict(r._fields['move_type']._description_selection(r.env)).get(r.move_type), r.partner_id.name, r.invoice_date.strftime("%d/%m/%Y")
            ))
        if errors:
            raise ValidationError('\n'.join(errors))


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
