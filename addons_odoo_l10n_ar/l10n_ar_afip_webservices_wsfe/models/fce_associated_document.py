# -*- encoding: utf-8 -*-

from l10n_ar_api.afip_webservices.wsfe.wsfe import WsfeAssociatedDocument
from odoo import models, fields, api


class FceAssociatedDocument(models.Model):

    _name = 'fce.associated.document'
    _description = 'Documento de FCE asociado'

    invoice_id = fields.Many2one(
        'account.move',
        'Documento',
        ondelete='cascade',
    )
    associated_invoice_id = fields.Many2one('account.move', 'Documento asociado', domain=[
        ('move_type', 'in', ['out_invoice', 'out_refund']),
        ('state', '=', ['posted'])
    ])
    point_of_sale = fields.Char('Punto de venta', required=True)
    document_number = fields.Char('Numero', required=True)
    document_code = fields.Char('Código comprobante', required=True)
    cuit_transmitter = fields.Char('Cuit emisor', required=True)
    date = fields.Date('Fecha', required=True)
    canceled = fields.Boolean('Rechazado por comprador?')

    @api.onchange('associated_invoice_id')
    def onchange_invoice_id(self):
        invoice_name = self.associated_invoice_id.name.split('-') if self.associated_invoice_id else ['']
        invoice_name = invoice_name[1] if len(invoice_name) > 1 else invoice_name[0]
        point_of_sale = self.associated_invoice_id.pos_ar_id.name.lstrip('0')\
            if self.associated_invoice_id.pos_ar_id else ''
        invoice_name = invoice_name.lstrip('0')
        self.update({
            'point_of_sale': point_of_sale,
            'document_code': self.associated_invoice_id.voucher_type_id.code,
            'document_number': invoice_name,
            'cuit_transmitter': self.associated_invoice_id.company_id.vat,
            'date': self.associated_invoice_id.invoice_date,
            'canceled': self.associated_invoice_id.fce_rejected,
        })
    
    def create_wsfe_associated_document(self):
        return WsfeAssociatedDocument(
            self.document_code,
            self.point_of_sale,
            self.document_number,
            self.cuit_transmitter,
            self.date
        )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
