# -*- encoding: utf-8 -*-

from odoo import models, fields


class DenominationFiscalPosition(models.Model):

    _name = 'denomination.fiscal.position'
    _description = 'Denominación de posiciones fiscales'

    # issue_fiscal_position_id = fields.Many2one(
    #     'ar.fiscal.position',
    #     'Posicion Fiscal emisora',
    #     ondelete='cascade',
    #     required=True
    # )
    # receipt_fiscal_position_id = fields.Many2one(
    #     'ar.fiscal.position',
    #     'Posicion Fiscal receptora',
    #     ondelete='cascade',
    #     required=True
    # )
    account_denomination_id = fields.Many2one(
        'account.denomination',
        'Denominacion',
        ondelete='restrict',
        required=True
    )

    # _sql_constraints = [(
    #     'unique',
    #     'unique(issue_fiscal_position_id, receipt_fiscal_position_id, account_denomination_id)',
    #     'Ya existe esa combinación de posicion fiscal/denominacion'
    # )]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
