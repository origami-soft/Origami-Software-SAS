# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

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
        pdf = request.env.ref(ext_id).sudo().render_qweb_pdf([picking_sudo.id])[0]
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
