# -*- encoding: utf-8 -*-

from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http
from odoo.http import request


class WebsiteSale(WebsiteSale):

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, **kw):
        """ Agrego las posiciones fiscales y tipos de documento al contexto del render para que se puedan elegir """
        res = super().address(**kw)
        res.qcontext['document_types'] = request.env['partner.document.type'].sudo().search([])
        res.qcontext['fiscal_positions'] = request.env['account.fiscal.position'].sudo().search([('company_id', 'in', (request.env.company.id, False))])
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
