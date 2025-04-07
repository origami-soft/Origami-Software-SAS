# -*- coding: utf-8 -*-

from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_arba_cot_enabled = fields.Boolean(
        "Usar COT de ARBA",
        help='Permite generar el COT de arba una vez que se han asignado '
        'números de remitos en las entregas',
        implied_group='l10n_ar_cot_arba.arba_cot_enabled',
    )
    cot_arba_key = fields.Char(
        related='company_id.cot_arba_key',
        readonly=False,
    )
    cot_path_type = fields.Selection(
        related='company_id.cot_path_type',
        readonly=False,
    )

    cot_partner_id = fields.Many2one(
        related='company_id.cot_partner_id',
        readonly=False,
    )

    cot_prod_no_term_dev = fields.Selection(
        related='company_id.cot_prod_no_term_dev',
        readonly=False,
    )


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
