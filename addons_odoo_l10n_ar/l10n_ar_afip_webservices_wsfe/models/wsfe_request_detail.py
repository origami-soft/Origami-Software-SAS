# -*- encoding: utf-8 -*-

from odoo import models, fields


class WsfeRequestDetail(models.Model):

    _name = 'wsfe.request.detail'
    _description = 'Detalle de wsfe request'

    request_sent = fields.Text('Request enviado', required=True)
    request_received = fields.Text('Request recibido', required=True)
    invoice_ids = fields.Many2many(
        'account.move',
        'invoice_request_details',
        'request_detail_id',
        'invoice_id',
        string='Documento'
    )
    result = fields.Char('Resultado')
    date = fields.Datetime('Fecha')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
