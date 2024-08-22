# -*- coding: utf-8 -*-
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

from odoo import api, models
from odoo.exceptions import UserError


class PosInvoiceReport(models.AbstractModel):
    _name = 'report.l10n_ar_electronic_invoice_report_pos.report_invoice'
    _description = 'Point of Sale Invoice Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """
        Copio un método de Odoo base que va a buscar las facturas correspondientes a los pedidos de POS para pasárselas
        al reporte (el reporte es de POS pero llama a templates de factura)
        """
        PosOrder = self.env['pos.order']
        ids_to_print = []
        invoiced_posorders_ids = []
        selected_orders = PosOrder.browse(docids)
        for order in selected_orders.filtered(lambda o: o.account_move):
            ids_to_print.append(order.account_move.id)
            invoiced_posorders_ids.append(order.id)
        not_invoiced_orders_ids = list(set(docids) - set(invoiced_posorders_ids))
        if not_invoiced_orders_ids:
            not_invoiced_posorders = PosOrder.browse(not_invoiced_orders_ids)
            not_invoiced_orders_names = [a.name for a in not_invoiced_posorders]
            raise UserError('Sin enlace a una factura para %s, ' % ', '.join(not_invoiced_orders_names))

        return {'docs': self.env['account.move'].sudo().browse(ids_to_print)}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
