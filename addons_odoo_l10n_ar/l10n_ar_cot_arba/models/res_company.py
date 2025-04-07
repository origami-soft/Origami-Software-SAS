# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import ValidationError

from l10n_ar_api.arba_webservices.cot.cot import ServicioCotArba

class ResCompany(models.Model):
    _inherit = 'res.company'

    cot_arba_key = fields.Char(
        'Clave COT',
        help='Clave para generación de Código de Operación Traslado (COT)',
    )

    cot_path_type = fields.Selection(
        [('U', 'Urbano'), ('R', 'Rural'), ('M', 'Mixto')],
        string='Tipo de Ruta',
        default='M',
    )

    cot_partner_id = fields.Many2one(
        'res.partner',
        string="Transportista",
    )

    cot_prod_no_term_dev = fields.Selection(
        [('0', 'No'), ('1', 'Si')],
        string='Productos no terminados / devoluciones',
        default='0',
    )

    def _get_arba_cot_details(self):
        self.ensure_one()
        return {
            'CUIT_EMPRESA': self.partner_id.vat, 
            'EMISOR_TENEDOR': '0',
        }

    def get_arba_service(self):
        type = self.env['ir.config_parameter'].sudo().get_param('l10n_ar_cot_arba.default_type_service')
        if not self.vat or not self.cot_arba_key:
            raise ValidationError('No se encontró una clave de ARBA o la compañía no tiene número de documento.')
        service = ServicioCotArba(self.vat, self.cot_arba_key, type)
        return service
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
