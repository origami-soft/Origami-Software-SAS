# -*- encoding: utf-8 -*-

from odoo import exceptions
from odoo.addons.sale_stock.controllers.portal import SaleStockPortal
from odoo.http import request, route


class SaleStockSelfprintPortal(SaleStockPortal):

    @route(['/my/picking/pdf/<int:picking_id>'], type='http', auth="public", website=True)
    def portal_my_picking_report(self, picking_id, access_token=None, **kw):
        """ Redefino el método del controlador para imprimir remitos desde portal.
        Así, en caso de ser un remito autoimpresor se imprimirá el reporte correspondiente """
        """ Print delivery slip for customer, using either access rights or access token
        to be sure customer has access """
        try:
            picking_sudo = self._stock_picking_check_access(picking_id, access_token=access_token)
        except exceptions.AccessError:
            return request.redirect('/my')
        # Obtengo la acción correspondiente del reporte a imprimir
        ext_id = picking_sudo._get_report_action()
        # print report as sudo, since it require access to product, taxes, payment term etc.. and portal does not have those access rights.
        pdf = request.env['ir.actions.report'].sudo()._render_qweb_pdf(ext_id, [picking_sudo.id])[0]
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
