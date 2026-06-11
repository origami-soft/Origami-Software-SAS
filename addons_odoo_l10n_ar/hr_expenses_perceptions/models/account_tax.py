# -*- coding: utf-8 -*-

from odoo import models


class AccountTax(models.Model):
    _inherit = 'account.tax'

    def compute_all(self, price_unit, currency=None, quantity=1.0, product=None, partner=None, is_refund=False,
                    handle_price_include=True, include_caba_tags=False, fixed_multiplicator=1):
        """Override to prevent force_price_include from affecting perception taxes.

        When force_price_include=True (e.g. from hr.expense), perception taxes should not be treated as
        price-included since their amount comes from perception_ctx and is not embedded in the price_unit.
        """
        force_price_include = self._context.get('force_price_include')
        perception_taxes = self.filtered(lambda t: t.amount_type == 'perception')

        if force_price_include and perception_taxes:
            regular_taxes = self - perception_taxes

            # Compute regular taxes with force_price_include (as intended by hr.expense)
            res = super(AccountTax, regular_taxes).compute_all(
                price_unit, currency=currency, quantity=quantity, product=product, partner=partner,
                is_refund=is_refund, handle_price_include=handle_price_include,
                include_caba_tags=include_caba_tags, fixed_multiplicator=fixed_multiplicator,
            )

            # Compute perceptions WITHOUT force_price_include so they are not extracted from the price
            perception_res = super(AccountTax, perception_taxes).with_context(
                force_price_include=False,
            ).compute_all(
                price_unit, currency=currency, quantity=quantity, product=product, partner=partner,
                is_refund=is_refund, handle_price_include=False,
                include_caba_tags=include_caba_tags, fixed_multiplicator=fixed_multiplicator,
            )

            # Merge perception tax lines into the result
            for tax_line in perception_res['taxes']:
                res['taxes'].append(tax_line)
                res['total_included'] += tax_line['amount']

            return res

        return super().compute_all(
            price_unit, currency=currency, quantity=quantity, product=product, partner=partner,
            is_refund=is_refund, handle_price_include=handle_price_include,
            include_caba_tags=include_caba_tags, fixed_multiplicator=fixed_multiplicator,
        )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: