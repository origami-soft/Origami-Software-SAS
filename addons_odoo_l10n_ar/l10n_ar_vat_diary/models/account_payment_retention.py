# -*- encoding: utf-8 -*-

from odoo import models
from odoo.exceptions import ValidationError


class AccountPaymentRetention(models.Model):
    _inherit = 'account.payment.retention'

    def _get_retention_currency_rate(self):
        """ Obtengo el rate de la retención """
        self.ensure_one()
        return self.rate if self.company_id.currency_id != self.currency_id else 1

    def update_vat_diary_values(self, taxes_position, vals, size_header):
        """Actualiza un diccionario con los datos de una fila del subdiario
        para las retenciones

        :param taxes_position: Diccionario con las posiciones de los
        impuestos en el subdiario
        :type taxes_position: dict
        :param vals: Diccionario con los datos de una fila del subdiario
        :type vals: dict
        :param size_header: Tamaño del encabezado genérico del subdiario
        :type size_header: int
        """

        rate = self._get_retention_currency_rate()
        tax_id = self.retention_id.get_taxes(self.company_id)
        try:
            vals[taxes_position[tax_id] + size_header] = round(self.amount * rate, 2)
        except Exception:
            raise ValidationError('No se encontro impuesto para la retencion {}'.format(self.retention_id.display_name))

    def get_vat_diary_total(self):
        self.ensure_one()
        return abs(self.amount) * self._get_retention_currency_rate()

    def get_vat_diary_name(self):
        self.ensure_one()
        if self.certificate_no:
            cert_split = self.certificate_no.split('-')
            return "RET {}".format(cert_split[0].zfill(5) + '-' + cert_split[1] if len(cert_split) == 2 else self.certificate_no)
        name_split = self.payment_id.name.split('-')
        return name_split[0].zfill(5) + '-' + name_split[1] if len(name_split) == 2 else self.payment_id.name

    def get_vat_diary_dict(self):
        """Devuelve los datos de una retención en un diccionario para el reporte de subdiario de IVA

        :return: Diccionario con datos de retención
        :rtype: dict
        """
        self.ensure_one()
        return {
            'id': self.id,
            'model': self._name,
            'type': 'retention',
            'date': self.date.strftime('%d/%m/%Y') or '',
            'partner': self.partner_id.name or '',
            'vat': self.partner_id.vat or '',
            'fiscal_position': self.partner_id.property_account_position_id.name or '',
            'voucher_type': 'Retención',
            'voucher': self.get_vat_diary_name(),
            'jurisdiction': dict(self._fields['jurisdiction'].selection).get(self.jurisdiction, ''),
            'retention': self.retention_id.name,
            'retention_id': self.retention_id.id,
            'total': self.get_vat_diary_total(),
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
