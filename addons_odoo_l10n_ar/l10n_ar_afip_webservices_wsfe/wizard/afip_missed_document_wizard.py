# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError
import zeep, ast
import requests
from ..models.document_book import SERVICE_FUNCTION

RESULT_KEYS = {
    'wsfe': 'ResultGet',
    'wsfex': 'FEXResultGet',
    'wsbfe': 'BFEResultGet',
}

CAE_KEYS = {
    'wsfe': 'CodAutorizacion',
    'wsfex': 'Cae',
    'wsbfe': 'Cae',
}


class AfipMissedDocumentWizard(models.TransientModel):
    _name = 'afip.missed.document.wizard'
    _description = 'Wizard de recupero de comprobantes'

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
            lambda x: x.book_type_id.is_electronic()
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
        document_book = self.pos_ar_id.document_book_ids.filtered(lambda l: l.voucher_type_id == self.voucher_type_id)
        if not document_book:
            raise ValidationError("El punto de venta {} no posee un talonario para {}".format(
                self.pos_ar_id.name, self.voucher_type_id.name
            ))
        service_str = SERVICE_FUNCTION.get(document_book.book_type_id.type)
        service = getattr(self.env['wsaa.configuration'], f'get_{service_str}')(self.company_id)

        default_cipher = requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'AES128-SHA'

        try:
            cae_request = service.retrieve_cae(self.voucher_type_id.code, self.document_number, self.pos_ar_id.name)[0]
        finally:
            requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = default_cipher

        self.response = None
        result_key = RESULT_KEYS[service_str]
        cae_key = CAE_KEYS[service_str]
        if cae_request.get(result_key) and cae_request[result_key].get(cae_key):
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
            document_book = self.pos_ar_id.document_book_ids.filtered(lambda l: l.voucher_type_id == self.voucher_type_id)
            service_str = SERVICE_FUNCTION.get(document_book.book_type_id.type)
            getattr(self, '_fill_{}_data'.format(service_str))(response)
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
    
    def _fill_wsfe_data(self, response):  # TODO: unificar los tres métodos
        invoice_date = datetime.strptime(
                response['ResultGet']['CbteFch'],
                '%Y%m%d'
            ) if response['ResultGet'].get('CbteFch') else None
        self.move_id.sudo().write({
            'cae': response['ResultGet']['CodAutorizacion'],
            'cae_due_date': datetime.strptime(response['ResultGet']['FchVto'], '%Y%m%d')
            if response['ResultGet'].get('FchVto') else None,
            'voucher_name': '{}-{}'.format(
                str(response['ResultGet']['PtoVta']).zfill(self.pos_ar_id.prefix_quantity or 0),
                str(response['ResultGet']['CbteHasta']).zfill(8)
            ),
            'invoice_date': invoice_date,
            'date': invoice_date
        })
    
    def _fill_wsfex_data(self, response):
        invoice_date = datetime.strptime(
                response['FEXResultGet']['Fecha_cbte'],
                '%Y%m%d'
            ) if response['FEXResultGet'].get('Fecha_cbte') else None
        self.move_id.sudo().write({
            'cae': response['FEXResultGet']['Cae'],
            'cae_due_date': datetime.strptime(response['FEXResultGet']['Fch_venc_Cae'], '%Y%m%d')
            if response['FEXResultGet'].get('Fch_venc_Cae') else None,
            'voucher_name': '{}-{}'.format(
                str(response['FEXResultGet']['Punto_vta']).zfill(self.pos_ar_id.prefix_quantity or 0),
                str(response['FEXResultGet']['Cbte_nro']).zfill(8)
            ),
            'invoice_date': invoice_date,
            'date': invoice_date
        })
    
    def _fill_wsbfe_data(self, response):
        invoice_date = datetime.strptime(
                response['BFEResultGet']['Fecha_cbte'],
                '%Y%m%d'
            ) if response['BFEResultGet'].get('Fecha_cbte') else None
        self.move_id.sudo().write({
            'cae': response['BFEResultGet']['Cae'],
            'cae_due_date': datetime.strptime(response['BFEResultGet']['Fch_venc_Cae'], '%Y%m%d')
            if response['BFEResultGet'].get('Fch_venc_Cae') else None,
            'voucher_name': '{}-{}'.format(
                str(response['BFEResultGet']['Punto_vta']).zfill(self.pos_ar_id.prefix_quantity or 0),
                str(response['BFEResultGet']['Cbte_nro']).zfill(8)
            ),
            'invoice_date': invoice_date,
            'date': invoice_date
        })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
