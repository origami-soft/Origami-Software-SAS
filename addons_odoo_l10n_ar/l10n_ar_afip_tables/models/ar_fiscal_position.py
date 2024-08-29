# -*- encoding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import ValidationError


class AccountFiscalPosition(models.Model):

    _inherit = 'ar.fiscal.position'

    denomination_fiscal_position_ids = fields.Many2one('denomination.fiscal.position', ondelete='restrict')
    denomination_fiscal_position_ids = fields.One2many(
        'denomination.fiscal.position',
        'issue_fiscal_position_id',
        'Denominaciones y posiciones fiscales',
        help="Desde aqui se realizan los mapeos para ver que tipo de documento se realizan"
             " a otras posiciones fiscales\npara cada denominacion"
    )

    def get_denomination(self, receipt_fiscal_position):
        """
        Busca la denominacion para la posicion fiscal que se pide
        :param receipt_fiscal_position: account.fiscal.position - Posicion fiscal receptora
        :return: account.denomination - Denominacion resultante
        """

        return self.denomination_fiscal_position_ids.filtered(
            lambda x: x.receipt_fiscal_position_id == receipt_fiscal_position
        ).account_denomination_id


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
