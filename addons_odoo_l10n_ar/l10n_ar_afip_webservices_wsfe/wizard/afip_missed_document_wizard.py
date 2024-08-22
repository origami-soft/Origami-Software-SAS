# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError
import zeep
import ast
import requests
import urllib3
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'AES128-SHA'


class AfipMissedDocumentWizard(models.TransientModel):

    _name = 'afip.missed.document.wizard'

    company_id = fields.Many2one(
        'res.company',
        'Empresa',
        default=lambda self: self.env.company
    )
    pos_ar_id = fields.Many2one(
        'pos.ar',
        'Punto de venta',
        required=True
    )
    available_voucher_type_ids = fields.Many2many(
        'voucher.type',
        compute='_compute_available_voucher_type_ids'
    )
    voucher_type_id = fields.Many2one(
        'voucher.type',
        'Tipo de comprobante',
        required=True
    )
    document_number = fields.Integer(
        'Numero de comprobante'
    )
    move_id = fields.Many2one(
        'account.move',
        'Documento a completar',
        help="El documento a seleccionar tiene que tener el punto de venta y tipo "
             "de comprobante que se seleccionó asociado"
    )
    response = fields.Text(
        'Respuesta'
    )
    response_data = fields.Text(
        'Datos a asignar',
    )

    @api.depends('pos_ar_id')
    def _compute_available_voucher_type_ids(self):
        self.available_voucher_type_ids = self.pos_ar_id.document_book_ids.filtered(
            lambda x: x.book_type_id.type == 'electronic'
        ).mapped('voucher_type_id')

    @api.onchange('pos_ar_id')
    def onchange_pos_ar_id(self):
        self.voucher_type_id = None

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.pos_ar_id = None

    @api.onchange('voucher_type_id')
    def onchange_pos_ar_id(self):
        self.response = None

    def get_documents_data(self):
        wsfe = self.env['wsfe.configuration'].get_wsfe(self.company_id)
        cae_request = wsfe.retrieve_cae(self.voucher_type_id.code, self.document_number, self.pos_ar_id.name)[0]
        self.response = None
        if cae_request.get('ResultGet') and cae_request['ResultGet'].get('CodAutorizacion'):
            self.response = zeep.helpers.serialize_object(cae_request, dict)
            """
            self.write({
                'cae': cae_request['ResultGet']['CodAutorizacion'],
                'cae_due_date': datetime.strptime(cae_request['ResultGet']['FchVto'], '%Y%m%d'),
            })
            """
        elif cae_request.get('Errors'):
            raise ValidationError(
                "No se ha podido recuperar el CAE de AFIP\n" + '\n'.join(e['Msg'] for e in cae_request['Errors']['Err'])
            )
        return {
            'type': 'ir.actions.act_window',
            'name': 'Comprobante a recuperar',
            'res_model': self._name,
            'views': [[False, "form"]],
            'res_id': self.id,
            'target': 'new'
        }

    def fill_data(self):  # TODO: Unificar con funcion _write_wsfe_details_on_invoice
        try:
            response = ast.literal_eval(self.response)
            invoice_date = datetime.strptime(
                    response['ResultGet']['FchProceso'][:8],
                    '%Y%m%d'
                ) if response['ResultGet'].get('FchProceso') else None
            self.move_id.sudo().write({
                'cae': response['ResultGet']['CodAutorizacion'],
                'cae_due_date': datetime.strptime(response['ResultGet']['FchVto'], '%Y%m%d')
                if response['ResultGet'].get('FchVto') else None,
                'voucher_name': '{}-{}'.format(
                    str(response['ResultGet']['PtoVta']).zfill(self.pos_ar_id.prefix_quantity or 0),
                    str(response['ResultGet']['CbteHasta']).zfill(8)
                ),
                'invoice_date': invoice_date
            })
            self.move_id.set_voucher_name()
        except Exception:
            raise ValidationError("No se pudieron completar los datos en el documento")

        return {
            'type': 'ir.actions.act_window',
            'name': 'Documento',
            'res_model': 'account.move',
            'views': [[False, "form"]],
            'res_id': self.move_id.id
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
