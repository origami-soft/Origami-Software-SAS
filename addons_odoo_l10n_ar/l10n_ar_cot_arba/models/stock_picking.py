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

import datetime

from odoo import models, fields
from odoo.exceptions import ValidationError

from l10n_ar_api.arba_webservices.cot.cot import CotHeader, CotRemito, CotProducto, CotFooter, GeneradorArchivoCot

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    unique_cot_number = fields.Char(
        'COT - Nro Único',
        help='Número único del último COT solicitado',
    )
    cot_voucher_number = fields.Char(
        'COT - Nro Comprobante',
        help='Número de comprobante del último COT solicitado',
    )
    cot = fields.Char(
        'COT',
        help='Número de COT del último COT solicitado',
    )

    def _action_done(self):
        res = super()._action_done()
        self.env.cr.commit()
        for picking in self:
            if picking.picking_type_id.get_cot_automatically and picking.company_id.cot_arba_key:
                self.env['arba.cot.wizard'].with_context(active_model=picking._name, active_ids=picking.ids).create({'amount': picking.insurance_value}).confirm()
        return res

    def _get_arba_cot_details(self):
        self.ensure_one()
        partner_id = self.picking_type_id.warehouse_id.partner_id or self.company_id.partner_id
        if not self.voucher_name or len(self.voucher_name.split('-')) != 2:
            raise ValidationError(f'El remito {self.voucher_name} no posee un nombre con formato valido: xxxxx-xxxxxxxx')
        prefix, number = self.voucher_name.split('-')
        return {
            'FECHA_EMISION': datetime.date.today().strftime('%Y%m%d'), # Formato: AAAAMMDD
            'HORA_SALIDA_TRANSPORTE': '',
            'CODIGO_UNICO': "%s%s%s" % (str(self.env.ref('l10n_ar_afip_tables.afip_voucher_type_091').code).rjust(3, '0'), prefix.rjust(5, '0'), number.rjust(8, '0')), # 3 pos. CODIGO AFIP 5 pos. PREFIJO 8 pos. NÚMERO
            'SUJETO_GENERADOR': 'E', # Valores posibles: E (emisor), D (destinatario)
            'ORIGEN_RAZON_SOCIAL': partner_id.name[:49],
            'ORIGEN_DOMICILIO_CALLE': partner_id.street[:39],
            'ORIGEN_DOMICILIO_NUMERO': '',
            'ORIGEN_DOMICILIO_COMPLE': 'S/N',
            'ORIGEN_DOMICILIO_PISO': '',
            'ORIGEN_DOMICILIO_DTO': '',
            'ORIGEN_DOMICILIO_BARRIO': '',
            'ORIGEN_DOMICILIO_CODIGOPOSTAL': partner_id.zip[:7],
            'ORIGEN_DOMICILIO_LOCALIDAD': partner_id.city[:49],
            'ORIGEN_DOMICILIO_PROVINCIA': partner_id.state_id.code,
            'RECORRIDO_LOCALIDAD': '',
            'RECORRIDO_CALLE': '',
            'RECORRIDO_RUTA': '',
            'PROPIO_DESTINO_DOMICILIO_CODIGO': '',
            'ENTREGA_DOMICILIO_ORIGEN': 'NO',
            'IMPORTE': '',
        }

    def _check_arba_cot_details(self):
        self.ensure_one()
        partner_id = self.picking_type_id.warehouse_id.partner_id or self.company_id.partner_id
        msg = f'El partner {partner_id.name} (Almacen/Compañia) presenta los siguientes problemas: \n'
        errors = False
        if not partner_id.street:
            msg += '\t - El campo de calle se encuentra vacio. \n'
            errors = True
        if not partner_id.zip:
            msg += '\t - El campo codigo postal se encuentra vacio. \n'
            errors = True
        if not partner_id.city:
            msg += '\t - El campo ciudad se encuentra vacio. \n'
            errors = True
        if not partner_id.state_id:
            msg += '\t - El campo provincia/estado se encuentra vacio. \n'
            errors = True
        return (errors, msg)

    def action_present_picking_to_arba(
            self, date_out, path_type, carrier_partner,
            vehicle_patent, coupled_patent, prod_no_term_dev, amount):
        self.ensure_one()

        if self.cot or self.cot_voucher_number or self.unique_cot_number:
            return True

        service = self.company_id.get_arba_service()

        if self.env.context.get('use_default_values', False):
            amount = str(int(round(self.insurance_value * 100.0)))
            carrier_partner = self.company_id.cot_partner_id

        msg_error = ''

        error_picking, msg_picking = self._check_arba_cot_details()
        error_partner, msg_partner = self.partner_id._check_arba_cot_details()

        msg_error += msg_picking if error_picking else ''
        msg_error += msg_partner if error_partner else ''

        generador = GeneradorArchivoCot()
        picking_details = self._get_arba_cot_details()
        partner_details = self.partner_id._get_arba_cot_details()
        company_details = self.company_id._get_arba_cot_details()

        if not error_picking and not error_partner:
            header = CotHeader()
            header.cuitEmpresa = company_details['CUIT_EMPRESA']
            generador.agregar_registro(header)

            remito = CotRemito()
            remito.fechaEmision = picking_details['FECHA_EMISION']
            remito.codigoUnico = picking_details['CODIGO_UNICO']
            remito.fechaSalidaTransporte = date_out
            remito.horaSalidaTransporte = picking_details['HORA_SALIDA_TRANSPORTE']
            remito.sujetoGenerador = picking_details['SUJETO_GENERADOR']
            remito.destinatarioConsumidorFinal = partner_details['DESTINATARIO_CONSUMIDOR_FINAL']
            remito.destinatarioTipoDocumento = partner_details['DESTINATARIO_TIPO_DOCUMENTO']
            remito.destinatarioDocumento = partner_details['DESTINATARIO_DOCUMENTO']
            remito.destinatarioCuit = partner_details['DESTINATARIO_CUIT']
            remito.destinatarioRazonSocial = partner_details['DESTINATARIO_RAZON_SOCIAL']
            remito.destinatarioTenedor = partner_details['DESTINATARIO_TENEDOR']
            remito.destinoDomicilioCalle = partner_details['DESTINO_DOMICILIO_CALLE']
            remito.destinoDomicilioNumero = partner_details['DESTINO_DOMICILIO_NUMERO']
            remito.destinoDomicilioComple = partner_details['DESTINO_DOMICILIO_COMPLE']
            remito.destinoDomicilioPiso = partner_details['DESTINO_DOMICILIO_PISO']
            remito.destinoDomicilioDto = partner_details['DESTINO_DOMICILIO_DTO']
            remito.destinoDomicilioBarrio = partner_details['DESTINO_DOMICILIO_BARRIO']
            remito.destinoDomicilioCodigoPostal = partner_details['DESTINO_DOMICILIO_CODIGOPOSTAL']
            remito.destinoDomicilioLocalidad = partner_details['DESTINO_DOMICILIO_LOCALIDAD']
            remito.destinoDomicilioProvincia = partner_details['DESTINO_DOMICILIO_PROVINCIA']
            remito.propioDestinoDomicilioCodigo = picking_details['PROPIO_DESTINO_DOMICILIO_CODIGO']
            remito.entregaDomicilioOrigen = picking_details['ENTREGA_DOMICILIO_ORIGEN']
            remito.origenCuit = company_details['CUIT_EMPRESA']
            remito.origenRazonSocial = picking_details['ORIGEN_RAZON_SOCIAL']
            remito.emisorTenedor = company_details['EMISOR_TENEDOR']
            remito.origenDomicilioCalle = picking_details['ORIGEN_DOMICILIO_CALLE']
            remito.origenDomicilioNumero = picking_details['ORIGEN_DOMICILIO_NUMERO']
            remito.origenDomicilioComple = picking_details['ORIGEN_DOMICILIO_COMPLE']
            remito.origenDomicilioPiso = picking_details['ORIGEN_DOMICILIO_PISO']
            remito.origenDomicilioDto = picking_details['ORIGEN_DOMICILIO_DTO']
            remito.origenDomicilioBarrio = picking_details['ORIGEN_DOMICILIO_BARRIO']
            remito.origenDomicilioCodigoPostal = picking_details['ORIGEN_DOMICILIO_CODIGOPOSTAL']
            remito.origenDomicilioLocalidad = picking_details['ORIGEN_DOMICILIO_LOCALIDAD']
            remito.origenDomicilioProvincia = picking_details['ORIGEN_DOMICILIO_PROVINCIA']
            remito.transportistaCuit = carrier_partner.vat
            remito.tipoRecorrido = path_type
            remito.recorridoLocalidad = picking_details['RECORRIDO_LOCALIDAD']
            remito.recorridoCalle = picking_details['RECORRIDO_CALLE']
            remito.recorridoRuta = picking_details['RECORRIDO_RUTA']
            remito.patenteVehiculo = vehicle_patent
            remito.patenteAcoplado = coupled_patent
            remito.productoNoTermDev = prod_no_term_dev
            remito.importe = amount
            generador.agregar_registro(remito)

        for move_line in self.mapped('move_lines').filtered(lambda x: x.product_uom_qty):
            move_error, msg_move = move_line._check_arba_cot_details()
            msg_error += msg_move if move_error else ''

            if not move_error:
                producto = CotProducto()
                stock_move_details = move_line._get_arba_cot_details()
                producto.codigoUnicoProducto = stock_move_details['CODIGO_UNICO_PRODUCTO']
                producto.arbaCodigoUnidadMedida = stock_move_details['ARBA_CODIGO_UNIDAD_MEDIDA']
                producto.cantidad = stock_move_details['CANTIDAD']
                producto.propioCodigoProducto = stock_move_details['PROPIO_CODIGO_PRODUCTO']
                producto.propioDescripcionProducto = stock_move_details['PROPIO_DESCRIPCION_PRODUCTO']
                producto.propioDescripcionUnidadMedida = stock_move_details['PROPIO_DESCRIPCION_UNIDAD_MEDIDA']
                producto.cantidadAjustada = stock_move_details['CANTIDAD_AJUSTADA']
                generador.agregar_registro(producto)

        if msg_error:
            raise ValidationError(msg_error)

        footer = CotFooter()
        footer.cantidadTotalRemitos = str(len(self))
        generador.agregar_registro(footer)

        if self.company_id:
            sequence_number = self.env['ir.sequence'].with_context(force_company=self.company_id.id).next_by_code('arba.cot.file')
        else:
            sequence_number = self.env['ir.sequence'].next_by_code('arba.cot.file')

        filename = "TB_%s_%s%s_%s_%s" % (
            company_details['CUIT_EMPRESA'],
            '000',
            '000',
            picking_details['FECHA_EMISION'],
            sequence_number)

        file = generador.generar_archivo(filename)

        response = service.presentar(file.name)

        if response.get('tipoError', False):
            raise ValidationError('Ocurrio el siguiente error: %s' % response.get('mensajeError'))
        elif response.get('errores', False):
            raise ValidationError(response.get('errores').values())

        file = open(file.name, 'r')
        content = file.read()


        attachments = [(f'{filename}.txt', content)]
        body = """
<p>
    Resultado solicitud COT:
    <ul>
        <li>Número Comprobante: %s</li>
        <li>Código Integridad: %s</li>
        <li>Procesado: %s</li>
        <li>Número Único: %s</li>
        <li>COT: %s</li>
    </ul>
</p>
""" % (response.get('numeroComprobante'), response.get('codigoIntegridad'),
            response.get('procesado'), response.get('numeroUnico'), response.get('cot'))

        self.write({
            'unique_cot_number': response.get('numeroComprobante'),
            'cot_voucher_number': response.get('numeroUnico'),
            'cot': response.get('cot'),
        })
        self.message_post(
            body=body,
            subject='Remito Electrónico Solicitado',
            attachments=attachments)

        # Hago un commit para asegurarme la escritura de ARBA 
        # al procesar varios remitos
        self.env.cr.commit()
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
