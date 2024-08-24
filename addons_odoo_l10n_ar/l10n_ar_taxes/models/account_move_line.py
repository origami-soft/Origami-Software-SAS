# -*- encoding: utf-8 -*-

from odoo import models, api
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    @api.constrains('tax_ids')
    def check_more_than_one_vat_in_line(self):
        """ Se asegura que no haya mas de un impuesto tipo IVA en las lineas de factura """
        for move_line in self:
            if len(move_line.tax_ids.filtered(lambda r: r.is_vat)) > 1:
                raise ValidationError("No puede haber mas de un impuesto de tipo IVA en una linea!")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
