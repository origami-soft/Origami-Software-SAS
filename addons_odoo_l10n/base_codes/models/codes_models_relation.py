# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

MODELS_WITH_COMPANY = ['account.tax']


class CodesModelsRelation(models.Model):
    """
    Intermediate table to assign models, code and application
    so every application that needs a specific code of a model
    doesn't have to write on the model table.
    """

    _name = 'codes.models.relation'
    _description = 'Relación codes-models'

    name = fields.Char('Aplicacion', required=True)
    name_model = fields.Char('Modelo', required=True)
    id_model = fields.Integer('Id del modelo', required=True)
    code = fields.Char('Codigo / Nombre', required=True)
    company_id = fields.Many2one(
        'res.company',
        'Compania',
    )

    @api.model_create_multi
    def create(self, vals_list):
        for r in vals_list:
            if not r.get('company_id') and r.get('name_model') in MODELS_WITH_COMPANY:
                r['company_id'] = self.env.company.id
        return super().create(vals_list)

    def get_record_from_code(self, name_model, code, name):
        """
        Busca el objeto segun el codigo de la aplicacion
        :param name: Aplicacion (ej: Afip, Uruware)
        :param name_model: Nombre del modelo (ej: account.invoice)
        :param code: Codigo de la aplicacion
        :return: record del objeto del name_model
        """
        record = self.search([
            ('name', '=', name),
            ('name_model', '=', name_model),
            ('code', '=', code)
        ], limit=1)

        if not record:
            raise ValidationError('No se encontro instancia para: \n Aplicacion {0}:'
                          '\nModelo: {1}\nCodigo: {2}'.format(name, name_model, code))

        return record.get_record()

    def get_code(self, name_model, id_model, name):
        """
        Busca el codigo de la aplicacion para los parametros definidos
        :param name: Aplicacion (ej: Afip, Uruware)
        :param name_model: Nombre del modelo (ej: account.invoice)
        :param id_model: Id a buscar
        :return: Codigo de la aplicacion
        """
        record = self.search([
            ('name', '=', name),
            ('name_model', '=', name_model),
            ('id_model', '=', id_model)
        ], limit=1)

        if not record:
            raise ValidationError('No se encontro codigo para: \n Aplicacion {0}:'
                          '\nModelo: {1}\nId: {2}'.format(name, name_model, id_model))

        return record.code

    def get_record(self):
        """ :return record: Objeto del modelo "name_model" con id "id_model" """

        try:
            record = self.env[self.name_model].browse(self.id_model)
        except KeyError:
            raise ValidationError("No existe el modelo {}".format(self.name_model))

        if not record:
            raise ValidationError("No se encontro el objeto con id: {} para el modelo {}".format(self.id_model, self.name_model))

        return record

    _sql_constraints = [
        ('Unique', 'unique(name, name_model, id_model)', "Ya existe un registro similar")
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
