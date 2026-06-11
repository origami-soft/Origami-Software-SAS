# -*- encoding: utf-8 -*-

from odoo import models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_combination_info(
        self, combination=False, product_id=False, add_qty=1.0,
        parent_combination=False, only_template=False,
    ):
        res = super()._get_combination_info(combination, product_id, add_qty, parent_combination, only_template)
        res['price_wo_tax'] = self._get_price_wo_tax(combination, product_id, add_qty, parent_combination, only_template)
        return res

    def _get_price_wo_tax(self, combination, product_id, add_qty, parent_combination, only_template):
        """ Replico el cálculo base para obtener el precio sin impuestos del producto en el e-commerce """
        combination = combination or self.env['product.template.attribute.value']
        parent_combination = parent_combination or self.env['product.template.attribute.value']
        website = self.env['website'].get_current_website().with_context(self.env.context)

        if not product_id and not combination and not only_template:
            combination = self._get_first_possible_combination(parent_combination)

        if only_template:
            product = self.env['product.product']
        elif product_id:
            product = self.env['product.product'].browse(product_id)
            if (combination - product.product_template_attribute_value_ids):
                # If the combination is not fully represented in the given product
                #   make sure to fetch the right product for the given combination
                product = self._get_variant_for_combination(combination)
        else:
            product = self._get_variant_for_combination(combination)

        product_or_template = product or self
        combination = combination or product.product_template_attribute_value_ids
        price_context = product_or_template._get_product_price_context(combination)
        product_or_template = product_or_template.with_context(**price_context)
        pricelist = website.pricelist_id
        currency = website.currency_id

        pricelist_price = pricelist._get_product_price(
            product=product_or_template,
            quantity=add_qty,
            target_currency=currency,
        )
        return pricelist_price

    def _get_sales_prices(self, pricelist, fiscal_position):
        res = super()._get_sales_prices(pricelist, fiscal_position)
        for tmpl_id in res.keys():
            res[tmpl_id]['price_wo_tax'] = self.browse(tmpl_id)._get_sale_price_wo_tax(pricelist)
        return res

    def _get_sale_price_wo_tax(self, pricelist):
        """ Replico el cálculo base para obtener el precio sin impuestos del producto en la grilla del e-commerce """
        pricelist and pricelist.ensure_one()
        pricelist = pricelist or self.env['product.pricelist']
        currency = pricelist.currency_id or self.env.company.currency_id

        sales_prices = pricelist._get_products_price(self, 1.0)
        show_discount = pricelist and pricelist.discount_policy == 'without_discount'
        show_strike_price = self.env.user.has_group('website_sale.group_product_price_comparison')

        base_sales_prices = self._price_compute('list_price', currency=currency)
        price_reduce = sales_prices[self.id]

        price_list_contains_template = currency.compare_amounts(price_reduce, base_sales_prices[self.id]) != 0

        if self.compare_list_price and show_strike_price and not price_list_contains_template:
            price_reduce = base_sales_prices[self.id]

        return price_reduce

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
