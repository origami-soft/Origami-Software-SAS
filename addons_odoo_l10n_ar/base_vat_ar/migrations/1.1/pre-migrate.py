#!/usr/bin/env python
# coding: utf-8

from odoo.upgrade import util


def migrate(cr, installed_version):
    util.remove_module(cr, 'l10n_ar_bo')
    util.remove_module(cr, 'l10n_ar_stock_bo')
    util.remove_module(cr, 'l10n_ar_website_sale_price')
    util.remove_module(cr, 'l10n_ar_afip_pos_invoicing')
    util.rename_module(cr, 'l10n_ar', 'l10n_ar_bo')
    util.rename_module(cr, 'l10n_ar_stock', 'l10n_ar_stock_bo')
    util.rename_module(cr, 'l10n_ar_website_sale', 'l10n_ar_website_sale_price')
    util.rename_module(cr, 'l10n_ar_pos_invoicing', 'l10n_ar_afip_pos_invoicing')
