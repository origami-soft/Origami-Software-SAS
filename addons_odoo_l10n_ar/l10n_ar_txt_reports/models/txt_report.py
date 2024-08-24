# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class TxtReport(models.AbstractModel):
    _name = "txt.report"
    _description = "Reporte TXT"

    date_from = fields.Date(string='Desde', required=True)
    date_to = fields.Date(string='Hasta', required=True)
    file = fields.Binary(string='Archivo', readonly=True)
    filename = fields.Char(string='Nombre Archivo')
    company_id = fields.Many2one(
        'res.company',
        string='Empresa',
        required=True,
        readonly=True,
        change_default=True,
        default=lambda self: self.env.company
    )

    @api.constrains('date_from', 'date_to')
    def check_date(self):
        if self.date_from > self.date_to:
            raise ValidationError('La fecha "desde" no puede ser mayor a la fecha "hasta"')
    
    @api.onchange('date_from')
    def onchange_date_from(self):
        self.date_to = self.get_date_to()
    
    def get_date_to(self):
        return self.date_from + relativedelta(months=1) - relativedelta(days=1) if self.date_from else False

    def validate_fields(self, record):
        raise NotImplementedError()
    
    def get_model(self):
        raise NotImplementedError()
    
    def get_domain(self):
        raise NotImplementedError()
    
    def sort_records(self, records):
        raise NotImplementedError()

    def search_records(self):
        records = self.get_model().search(self.get_domain())
        return self.sort_records(records)
    
    def get_presentation(self):
        raise NotImplementedError()
    
    def get_filename(self):
        raise NotImplementedError()

    def generate_file(self):
        lines = self.get_presentation()
        errors = []
        for r in self.search_records():
            errors += self.validate_fields(r)
            if errors:
                continue
            try:
                self.create_line(lines, r)
            except ValidationError as e:
                raise e
            except Exception as e:
                raise ValidationError(e)
        if errors:
            # Casteo a set así, en caso de que varios registros hayan dado el mismo error, se muestre una vez sola
            errors = set(errors)
            raise ValidationError("\n".join(errors))
        else:
            self.file = lines.get_encoded_string()
            self.filename = self.get_filename()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
