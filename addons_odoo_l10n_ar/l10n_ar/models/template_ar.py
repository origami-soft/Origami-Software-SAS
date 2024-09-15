# -*- encoding: utf-8 -*-

from odoo import models
from odoo.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'

    @template('ar')
    def _get_ar_template_data(self):
        return {
            'property_account_receivable_id': 'creditos_por_ventas',
            'property_account_payable_id': 'proveedores',
            'property_account_expense_categ_id': 'otros_gastos_de_comercializacion',
            'property_account_income_categ_id': 'ventas_de_bienes',
            'property_tax_receivable_account_id': 'iva_credito_fiscal',
            'property_tax_payable_account_id': 'iva_debito_fiscal',
            'code_digits': '12',
            'visible': True,
        }
    
    @template('ar', 'res.company')
    def _get_ar_base_res_company(self):
        return {
            self.env.company.id: {
                'account_fiscal_country_id': 'base.ar',
                'bank_account_code_prefix': '1113',
                'cash_account_code_prefix': '1111',
                'transfer_account_code_prefix': '1119',
                'account_default_pos_receivable_account_id': 'creditos_por_ventas_punto_de_venta',
                'income_currency_exchange_account_id': 'ganancia_por_diferencias_de_cambio',
                'expense_currency_exchange_account_id': 'perdidas_por_diferencias_de_cambio',
            },
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
