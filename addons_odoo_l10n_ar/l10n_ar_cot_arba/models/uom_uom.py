# -*- coding: utf-8 -*-

from odoo import fields, models


class UomUom(models.Model):
    _inherit = 'uom.uom'

    arba_uom_code = fields.Char('Código unidad de medida ARBA')

    def action_arba_codes(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': 'http://www.arba.gov.ar/bajadas/Fiscalizacion/Operativos/TransporteBienes/Documentacion/20080701-TB-TablasDeValidacion.pdf',
            'target': 'new'
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
