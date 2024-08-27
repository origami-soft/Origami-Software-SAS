# -*- encoding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_l10n_ar_stock_picking_report = fields.Boolean(
        string="Remito autoimpresor")
    module_l10n_ar_selfprint_delivery_address = fields.Boolean(
        string="Transportista en  remito")
    module_l10n_ar_selfprint_merchandise_value = fields.Boolean(
        string="Remito valorizado")
    module_l10n_ar_bank_reconcile = fields.Boolean(
        string="Conciliación Bancaria")
    module_l10n_credit_cards = fields.Boolean(string="Tarjetas de Crédito")
    module_account_financial_report = fields.Boolean(
        string="Reportes de comunidad en contabilidad")
    module_l10n_ar_electronic_invoice_report_sale_stock = fields.Boolean(
        string="Lotes en facturas")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
