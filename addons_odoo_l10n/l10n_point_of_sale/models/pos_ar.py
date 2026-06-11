# -*- encoding: utf-8 -*-

from odoo import models, fields

class PosAr(models.Model):
    _name = 'pos.ar'
    _description = 'Punto de venta'

    name = fields.Char(
        string='Nombre',
        required=True
    )
    description = fields.Char(
        string='Descripcion'
    )
    document_book_ids = fields.One2many(
        comodel_name='document.book',
        inverse_name='pos_ar_id',
        string='Talonarios'
    )
    active = fields.Boolean(
        string='Activo',
        default=True
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañia',
        required=True,
        default=lambda self: self.env.company,
    )

    def get_available_documents(self, params):
        """Devuelve los talonarios que coincidan con los parámetros de params, 
        para ser usado como valor por defecto. 
        Estos inicialmente serán la categoría y las denominaciones, 
        siendo estas últimas agregadas por cada localización.

        :param params: Diccionario con los parámetros
        :type params: dict()
        :return: Talonarios encontrados
        :rtype: document.book()
        """        
        self.ensure_one()
        return self.document_book_ids.filtered(
            lambda db:
            (db.category == params.get('category') if 'category' in params else True) and
            (db.voucher_type_id.denomination_id.id in params.get('denomination_ids') if 'denomination_ids' in params else True)
        )

    def get_default_document_book(self, params):
        """Devuelve un talonario que coincida con los parámetros de params 
        y tenga la mayor precedencia, para ser usado como valor por defecto. 
        Estos inicialmente serán la categoría (obligatoriamente), y las 
        denominaciones de forma opcional, para que cada localización 
        agregue sus propias denominaciones de filtro.

        :param params: Diccionario con los parámetros
        :type params: dict()
        :return: Talonario encontrado
        :rtype: document.book()
        """        
        self.ensure_one()
        dbooks = self.get_available_documents(params)
        if not dbooks:
            return None
        return dbooks.sorted('sequence')[0]

    _sql_constraints = [
        ('type_unique', 'unique(name, company_id)', 'Ya existe un punto de venta con ese nombre para esta empresa')
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
