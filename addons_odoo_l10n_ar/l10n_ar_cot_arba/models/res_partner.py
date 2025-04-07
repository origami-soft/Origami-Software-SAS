# -*- coding: utf-8 -*-

from odoo import models

DOCUMENT_TYPE = {
        'DNI': 'DNI', 
        'Pasaporte': 'PAS',
        'CDI': 'CI',
        'LC': 'LC',
        'LE': 'LE'
    }

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_arba_cot_details(self):
        self.ensure_one()
        return {
            'DESTINATARIO_CONSUMIDOR_FINAL': '1' if self._is_final_consumer() else '0', # 0 = NO / 1 = SI
            'DESTINATARIO_TIPO_DOCUMENTO': self._return_valid_document_type(), # Valores posibles: ‘DNI’, ‘LC’, ‘LE’, ‘PAS’, ‘CI’
            'DESTINATARIO_DOCUMENTO': self._return_valid_document_type() and self.commercial_partner_id.vat or '', # Valores posibles: blanco o numero > 0
            'DESTINATARIO_CUIT': '' if self._is_final_consumer() else self.commercial_partner_id.vat, # Requerido si consumidor final=0
            'DESTINATARIO_RAZON_SOCIAL': self.name[:49], # Requerido si consumidor final = 0
            'DESTINATARIO_TENEDOR': '0' if self._is_final_consumer() else '1', # Si DESTINATARIO_CONSUMIDOR_FINAL=1 entonces DESTINATARIO_TENEDOR=0
            'DESTINO_DOMICILIO_CALLE': self.street[:39],
            'DESTINO_DOMICILIO_NUMERO': '', # 0 (cero) ó ‘ ’ (blanco) si DESTINO_DOMICILIO_COMPLE=‘S/N’
            'DESTINO_DOMICILIO_COMPLE': 'S/N', # Valores posibles: ‘ ’, ‘S/N’ , ‘1/2’, ‘1/4’, ‘BIS’
            'DESTINO_DOMICILIO_PISO': '',
            'DESTINO_DOMICILIO_DTO': '',
            'DESTINO_DOMICILIO_BARRIO': '',
            'DESTINO_DOMICILIO_CODIGOPOSTAL': self.zip[:7],
            'DESTINO_DOMICILIO_LOCALIDAD': self.city[:49],
            'DESTINO_DOMICILIO_PROVINCIA': self.state_id.code, # Válido según Tabla de Provincias
        }
    
    def _is_final_consumer(self):
        self.ensure_one()
        return self.property_account_position_id.ar_fiscal_position_id.id == self.env.ref('l10n_ar.ar_fiscal_position_cf').id

    def _return_valid_document_type(self):
        self.ensure_one()
        return DOCUMENT_TYPE.get(self.partner_document_type_id.name, '')

    def _check_arba_cot_details(self):
        self.ensure_one()
        msg = f'El partner {self.name} presenta los siguientes problemas: \n'
        errors = False
        if not self.street:
            msg += '\t - El campo de dirección se encuentra vacio. \n'
            errors = True
        if not self.zip:
            msg += '\t - El campo codigo postal se encuentra vacio. \n'
            errors = True
        if not self.city:
            msg += '\t - El campo ciudad se encuentra vacio. \n'
            errors = True
        if not self.state_id:
            msg += '\t - El campo provincia/estado se encuentra vacio. \n'
            errors = True
        if not self.property_account_position_id:
            msg += '\t - El campo posición fiscal no se encuentra establecido. \n'
            errors = True
        if not self.vat:
            msg += '\t - El campo número documento no se encuentra establecido. \n'
            errors = True
        return (errors, msg)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
