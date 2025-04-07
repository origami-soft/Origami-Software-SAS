# -*- coding: utf-8 -*-

import re

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ArbaCotWizard(models.TransientModel):
    _name = 'arba.cot.wizard'
    _description = 'arba.cot.wizard'

    def _default_date_out(self):
        return fields.Date.today()

    def _default_path_type(self):
        picking = self.env['stock.picking'].browse(self._context.get('active_id'))
        return picking.company_id.cot_path_type

    def _default_partner_id(self):
        picking = self.env['stock.picking'].browse(self._context.get('active_id'))
        return picking.company_id.cot_partner_id.id

    def _default_prod_no_term_dev(self):
        picking = self.env['stock.picking'].browse(self._context.get('active_id'))
        return picking.company_id.cot_prod_no_term_dev

    date_out = fields.Date(
        required=True,
        string='Fecha Salida',
        help='Debe ser mayor o igual a la fecha actual, y menor o igual a la fecha actual más treinta días.',
        default=lambda l: l._default_date_out()
    )

    path_type = fields.Selection(
        [('U', 'Urbano'), ('R', 'Rural'), ('M', 'Mixto')],
        string='Tipo de Ruta',
        required=True,
        default=lambda l: l._default_path_type(),
    )

    partner_id = fields.Many2one(
        'res.partner',
        string="Transportista",
        required=True,
        default=lambda l: l._default_partner_id()
    )
    
    vehicle_patent = fields.Char(
        string='Patente del Vehiculo',
        help='Requerido si CUIT Transportista = CUIT Compañía\n'
        '3 letras y 3 numeros o 2 letras, 3 números y 2 letras'
    )

    coupled_patent = fields.Char(
        string='Patente del Acoplado',
        help='3 letras y 3 numeros o 2 letras, 3 números y 2 letras'
    )

    prod_no_term_dev = fields.Selection(
        [('0', 'No'), ('1', 'Si')],
        string='Productos no terminados / devoluciones',
        default=lambda l: l._default_prod_no_term_dev(),
        required=True,
    )

    amount = fields.Float(
        string='Importe Neto',
    )

    @api.constrains('vehicle_patent', 'coupled_patent')
    def check_vehicle_patent(self):
        pattern = re.compile(r'^[A-Z]{2}\d{3}[A-Z]{2}$|^[A-Z]{3}\d{3}$')
        msg = ''
        for record in self:
           if record.vehicle_patent and not pattern.match(record.vehicle_patent):
               msg += "La patente del vehículo no es válida. Debe ser 3 letras y 3 números o 2 letras, 3 números y 2 letras. \n"
           if record.coupled_patent and not pattern.match(record.coupled_patent):
               msg += "La patente del vehículo acoplado no es válida. Debe ser 3 letras y 3 números o 2 letras, 3 números y 2 letras. \n"
           if msg:
               raise ValidationError(msg)

    @api.constrains('date_out')
    def check_date_out(self):
        today = fields.Date.today()
        thirty_days_later = fields.Date.add(today, days=30)
        for record in self:
            if record.date_out < today or record.date_out > thirty_days_later:
                raise ValidationError("La fecha de salida no es válida. Debe ser mayor o igual a la fecha actual, y menor o igual a la fecha actual más treinta días.")

    @api.constrains('partner_id')
    def check_partner_id(self):
        for record in self:
            if not record.partner_id.vat:
                raise ValidationError(f'El transportista {record.partner_id.name} no tiene número de documento establecido.')

    def confirm(self):
        self.ensure_one()
        if self._context.get('active_model') != 'stock.picking':
            return True
        pickings = self.env['stock.picking'].browse(self._context.get('active_ids'))
        for picking in pickings:
            picking.action_present_picking_to_arba(
                self.date_out.strftime('%Y%m%d'), self.path_type,
                self.partner_id, self.vehicle_patent or '',
                self.coupled_patent or '', self.prod_no_term_dev, str(int(round(self.amount * 100.0))))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
