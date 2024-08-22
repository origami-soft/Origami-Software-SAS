# -*- encoding: utf-8 -*-

from odoo import models


class PerceptionPerception(models.Model):

    _inherit = 'perception.perception'

    def get_afip_code(self):
        """ Devuelve el codigo de AFIP en base a la jurisdiccion """
        self.ensure_one()
        codes = {
            ('gross_income', 'nacional'): 1,
            ('gross_income', 'provincial'): 2,
            ('gross_income', 'municipal'): 3,
            ('vat', 'nacional'): 6,
        }
        return codes.get((self.type, self.jurisdiction))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
