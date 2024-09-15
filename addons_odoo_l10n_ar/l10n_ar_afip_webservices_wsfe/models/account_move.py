# -*- encoding: utf-8 -*-

import ast, pytz, zeep
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from l10n_ar_api import documents
from l10n_ar_api.afip_webservices import wsfe, wsfex, wsbfe
from odoo import models, fields, registry, api
from odoo.exceptions import ValidationError
import requests


class AccountMove(models.Model):

    _inherit = 'account.move'

    date_service_from = fields.Date('Fecha servicio inicial', help='Fecha inicial del servicio brindado', copy=False)
    date_service_to = fields.Date('Fecha servicio final', help='Fecha final del servicio brindado', copy=False)
    cae = fields.Char('CAE', readonly=True, copy=False)
    cae_due_date = fields.Date('Vencimiento CAE', readonly=True, copy=False)
    wsfe_request_detail_ids = fields.Many2many(
        'wsfe.request.detail',
        'invoice_request_details',
        'invoice_id',
        'request_detail_id',
        string='Detalles Wsfe',
        copy=False,
    )
    company_partner_id = fields.Many2one(related='company_id.partner_id', string='Partner compania')
    cbu_partner_bank_id = fields.Many2one('res.partner.bank', 'Cuenta bancaria')
    cbu_transmitter = fields.Char('CBU Emisor')
    fce_associated_document_ids = fields.One2many('fce.associated.document', 'invoice_id', 'Documentos asociados')
    fce_rejected = fields.Boolean('¿Rechazada por el comprador?')
    transfer_option = fields.Selection(
        selection=[('SCA', 'Sistema de circulación abierta'),
                   ('ADC', 'Agente de depósito colectivo')],
        string="Opción de transferencia",
        copy=False
    )

    def _get_integrity_hash_fields(self):
        if self._context.get('is_written_from_afip'):
            return ['journal_id', 'company_id']
        return super()._get_integrity_hash_fields()

    def _check_electronic_invoice_sent(self):
        return any(move.cae for move in self)
    
    @api.onchange('cbu_partner_bank_id')
    def onchange_partner_bank_id(self):
        self.cbu_transmitter = self.cbu_partner_bank_id.cbu

    def action_switch_invoice_into_refund_credit_note(self):
        if any(move.wsfe_request_detail_ids.filtered(lambda x: x.result == 'A') or move.cae for move in self):
            raise ValidationError("No se puede usar esta acción con un documento enviado a AFIP!")
        return super(AccountMove, self).action_switch_invoice_into_refund_credit_note()
    
    def _update_document_book_and_commit(self):
        dbook_cr = registry(self.env.cr.dbname).cursor()
        # Por alguna razón, si llamo al método next_number del talonario, no se guardan los cambios. Así que lo hago
        # directamente con el cursor
        dbook_cr.execute("update document_book set last_number = cast(cast(last_number as integer) + 1 as varchar) where id = {}".format(
            self.document_book_id.id
        ))
        dbook_cr.commit()
        dbook_cr.close()
    
    def _auto_compute_invoice_reference(self):
        """ Heredo este método para no utilizar el completado base de payment_reference cuando se validen facturas
        electrónicas y completarlo a mano cuando se vuelquen los detalles recibidos por AFIP
        """
        return not self.document_book_id.book_type_id.is_electronic() and super()._auto_compute_invoice_reference()

    def action_electronic(self):
        """
        Realiza el envio a AFIP de la factura y escribe en la misma el CAE y su fecha de vencimiento.
        :raises ValidationError: Si el talonario configurado no tiene la misma numeracion que en AFIP.
                                 Si hubo algun error devuelto por afip al momento de enviar los datos.
        """
        self = self.with_context(is_written_from_afip=True)
        electronic_invoices = []
        pos = self.document_book_id.pos_ar_id
        invoices = self.filtered(lambda l: not l.cae and l.amount_total and l.pos_ar_id == pos).sorted(lambda l: l.id)
        sent_invoices = invoices.filtered(lambda x: any(request.result == 'A' for request in x.wsfe_request_detail_ids))
        invoices -= sent_invoices

        # Si hubo un problema despues de escribir una respuesta y no se llegaron a escribir los detalles en las facturas
        for invoice in sent_invoices:
            invoice._write_wsfe_details_on_invoice(
                ast.literal_eval(
                    invoice.wsfe_request_detail_ids.filtered(lambda x: x.result == 'A')[0].request_received
                ))

        if invoices:
            afip_wsfe = self._get_wsfe()

        for invoice in invoices:
            # Validamos los campos
            invoice._validate_required_electronic_fields()

            # Obtenemos el codigo de comprobante
            document_afip_code = invoice.get_document_afip_code(self.document_book_id)
            new_cr = registry(self.env.cr.dbname).cursor()
            # Validamos que la factura se encuentre en la base de datos
            try:
                self.with_env(self.env(cr=new_cr))._is_invoice_in_db(invoice)
            except Exception as e:
                new_cr.close()
                raise ValidationError(e.args)
            # Validamos la numeracion
            self.document_book_id.with_env(self.env(cr=new_cr)).action_wsfe_number(afip_wsfe, document_afip_code)
            new_cr.close()
            # Armamos la factura
            electronic_invoices.append(invoice._set_electronic_invoice_details(document_afip_code))

        if electronic_invoices:
            response = None

            default_cipher = requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS
            requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'AES128-SHA'
            # Chequeamos la conexion y enviamos las facturas a AFIP, guardando el JSON enviado, el response y mostrando
            # los errores (en caso de que los haya)
            try:
                afip_wsfe.check_webservice_status()
                response, invoice_detail = afip_wsfe.get_cae(electronic_invoices, pos.name)
                afip_wsfe.show_error(response)
            except Exception as e:
                raise ValidationError(e.args)
            finally:
                requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = default_cipher
                # Commiteamos para que no haya inconsistencia con la AFIP.
                if response and response.FeDetResp:
                    response_cr = registry(self.env.cr.dbname).cursor()
                    invoices.with_env(self.env(cr=response_cr)).write_wsfe_response(invoice_detail, response)
                    response_cr.commit()
                    response_cr.close()

            if response and response.FeCabResp and response.FeCabResp.Resultado != 'R':
                for invoice in invoices:
                    invoice._update_document_book_and_commit()
                    invoice._write_wsfe_details_on_invoice(zeep.helpers.serialize_object(response))

            if response and response.FeCabResp and response.FeCabResp.Resultado == 'R':
                # Traemos el conjunto de errores
                errores = '\n'.join(obs.Msg for obs in response.FeDetResp.FECAEDetResponse[0].Observaciones.Obs) \
                    if hasattr(response.FeDetResp.FECAEDetResponse[0], 'Observaciones') else ''
                raise ValidationError('Hubo un error al intentar validar el documento\n{0}'.format(errores))
        self.env.cr.commit()

    def _is_invoice_in_db(self, invoice):
        """
        Chequea la existencia del ID de la factura en la Base de Datos.
        :param invoice: Record de la factura.
        :raise: Exception si no la encuentra.
        """
        if not self.search([('id', '=', invoice.id)]):
            raise Exception("Error: el ID del registro no se encuentra en la base de datos")

    def write_wsfe_response(self, invoice_detail, response):
        """ Escribe el envio y respuesta de un envio a AFIP """
        if response.FeCabResp:
            # Nos traemos el offset de la zona horaria para dejar en la base en UTC como corresponde
            offset = datetime.now(pytz.timezone('America/Argentina/Buenos_Aires')).utcoffset().total_seconds() / 3600
            fch_proceso = datetime.strptime(response.FeCabResp.FchProceso, '%Y%m%d%H%M%S') - relativedelta(hours=offset)
            result = response.FeCabResp.Resultado
            date = fch_proceso
        else:
            result = "Error"
            date = fields.Datetime.now()

        self.env['wsfe.request.detail'].sudo().create({
            'invoice_ids': [(4, invoice.id) for invoice in self],
            'request_sent': invoice_detail,
            'request_received': response,
            'result': result,
            'date': date,
        })

    def _write_wsfe_details_on_invoice(self, response):
        self.ensure_one()
        # Busco, dentro del detalle de la respuesta, el segmento correspondiente a la factura
        cab = response.get('FeCabResp', {})
        det = response.get('FeDetResp', {}).get('FECAEDetResponse', [])[0]
        if cab.get('Resultado') == 'A':
            voucher_name = '{}-{}'.format(
                str(cab.get('PtoVta')).zfill(self.pos_ar_id.prefix_quantity or 0),
                str(det.get('CbteHasta')).zfill(8)
            )
            inv_date = datetime.strptime(det['CbteFch'], '%Y%m%d') if det.get('CbteFch') else None
            name_prefix = self.voucher_type_id.prefix + ' ' if self.voucher_type_id.prefix else ''
            inv_name = f"{name_prefix}{voucher_name or ''}"
            self.write({
                'cae': det.get('CAE'),
                'cae_due_date': datetime.strptime(det['CAEFchVto'], '%Y%m%d') if det.get('CAEFchVto') else None,
                'voucher_name': voucher_name,
                'payment_reference': inv_name,
                'invoice_date': inv_date,
                'date': inv_date,
            })

    def _write_wsfex_details_on_invoice(self, response):
        self.ensure_one()
        # Busco, dentro del detalle de la respuesta, el segmento correspondiente a la factura
        auth = response.get('FEXResultAuth', {})
        if auth.get('Resultado') == 'A':
            voucher_name = '{}-{}'.format(
                str(auth.get('Punto_vta')).zfill(self.pos_ar_id.prefix_quantity or 0),
                str(auth.get('Cbte_nro')).zfill(8)
            )
            inv_date = datetime.strptime(auth['Fch_cbte'], '%Y%m%d') if auth.get('Fch_cbte') else None
            name_prefix = self.voucher_type_id.prefix + ' ' if self.voucher_type_id.prefix else ''
            inv_name = f"{name_prefix}{voucher_name or ''}"
            self.write({
                'cae': auth.get('Cae'),
                'cae_due_date': datetime.strptime(auth['Fch_venc_Cae'], '%Y%m%d') if auth.get('Fch_venc_Cae') else None,
                'voucher_name': voucher_name,
                'payment_reference': inv_name,
                'invoice_date': inv_date,
                'date': inv_date,
            })

    def _write_wsbfe_details_on_invoice(self, request, response):
        # Busco, dentro del detalle de la respuesta, el segmento correspondiente a la factura
        auth = response.get('BFEResultAuth', {})
        if auth.get('Resultado') == 'A':
            voucher_name = '{:0>{prefix_qty}}-{:0>8}'.format(
                request.get('Punto_vta'),
                request.get('Cbte_nro'),
                prefix_qty=self.pos_ar_id.prefix_quantity or 0
            )
            inv_date = datetime.strptime(auth['Fch_cbte'], '%Y%m%d') if auth.get('Fch_cbte') else None
            name_prefix = self.voucher_type_id.prefix + ' ' if self.voucher_type_id.prefix else ''
            inv_name = f"{name_prefix}{voucher_name or ''}"
            self.write({
                'cae': auth.get('Cae'),
                'cae_due_date': datetime.strptime(auth['Fch_venc_Cae'], '%Y%m%d') if auth.get('Fch_venc_Cae') else None,
                'voucher_name': voucher_name,
                'payment_reference': inv_name,
                'invoice_date': inv_date,
                'date': inv_date,
            })

    def _set_electronic_invoice_details(self, document_afip_code):
        """ Mapea los valores de ODOO al objeto ElectronicInvoice"""

        self._set_empty_invoice_details()
        denomination_c = self.env.ref('l10n_ar_afip_tables.account_denomination_c')
        codes_models_proxy = self.env['codes.models.relation']

        # Seteamos los campos generales de la factura
        electronic_invoice = wsfe.invoice.ElectronicInvoice(document_afip_code)
        # Para comprobantes C solo se informa el importe total conciliado que corresponde con el taxed_amount de la API
        electronic_invoice.taxed_amount = self.amount_to_tax if self.voucher_type_id.denomination_id != denomination_c else self.amount_total
        electronic_invoice.untaxed_amount = self.amount_not_taxable if self.voucher_type_id.denomination_id != denomination_c else 0
        electronic_invoice.exempt_amount = self.amount_exempt if self.voucher_type_id.denomination_id != denomination_c else 0
        electronic_invoice.document_date = self.invoice_date or fields.Date.context_today(self)
        if codes_models_proxy.get_code('afip.concept', self.afip_concept_id.id, 'Afip') in ['2', '3']:
            electronic_invoice.service_from = self.date_service_from or fields.Date.context_today(self)
            electronic_invoice.service_to = self.date_service_to or fields.Date.context_today(self)
        electronic_invoice.payment_due_date = self.invoice_date_due or fields.Date.context_today(self)
        electronic_invoice.customer_document_number = self.partner_id.vat
        electronic_invoice.customer_document_type = codes_models_proxy.get_code(
            'partner.document.type',
            self.partner_id.partner_document_type_id.id,
            'Afip'
        )
        electronic_invoice.mon_id = self.env['codes.models.relation'].get_code(
            'res.currency',
            self.currency_id.id,
            'Afip'
        )
        electronic_invoice.mon_cotiz = self.currency_rate or self.current_currency_rate
        electronic_invoice.concept = int(codes_models_proxy.get_code(
            'afip.concept',
            self.afip_concept_id.id,
            'Afip'
        ))
        # Agregamos impuestos y percepciones
        self._add_vat_to_electronic_invoice(electronic_invoice)
        self._add_other_tributes_to_electronic_invoice(electronic_invoice)
        # Agregamos los documentos asociados para Notas de débito o crédito
        self._add_associated_documents_to_electronic_invoice_refund(electronic_invoice)
        # Agregamos lo exclusivo de facturas de crédito
        self._add_optionals_to_credit_invoice(electronic_invoice)
        return electronic_invoice

    def _add_associated_documents_to_electronic_invoice_refund(self, electronic_invoice):
        """ Agrega los documentos asociados para facturas cuando se envíen notas de débito o crédito """
        if self.is_debit_note or self.move_type == 'out_refund':
            if not self.fce_associated_document_ids:
                electronic_invoice.period_from = self.invoice_date or fields.Date.context_today(self)
                electronic_invoice.period_to = self.invoice_date or fields.Date.context_today(self)
            else:
                electronic_invoice.associated_documents = list(map(lambda assoc_doc: assoc_doc.create_wsfe_associated_document(), self.fce_associated_document_ids))

    def _add_optionals_to_credit_invoice(self, electronic_invoice):
        """ Agrega los opcionales para facturas de credito """
        if self.is_credit_invoice:
            if self.is_debit_note or self.move_type == 'out_refund':
                canceled = 'S' if any(self.fce_associated_document_ids.mapped('canceled')) else 'N'
                # Hay que informar el opcional de si el comprobante fue o no anulado por el comprador (ID 22)
                electronic_invoice.array_optionals = [wsfe.wsfe.WsfeOptional(22, canceled)]
            else:
                # 2101 es para CBU, como por ahora solo vamos a enviar ese opcional lo dejamos así. Si el día de mañana
                # vamos a utilizar mas opcionales habría que crear el modelo y mapeo necesario.
                # 27 es la opción de la transferencia, se puede informar que la factura se envíe al sistema de circulación
                # abierta o a un agente de depósito colectivo.
                if not self.cbu_transmitter:
                    raise ValidationError("Para enviar una Factura de crédito es necesario cargar CBU Emisor")
                if not self.transfer_option:
                    raise ValidationError("Para enviar una Factura de crédito es necesario informar \
                                           si se utiliza el Sistema de circulación abierta o Agente de depósito colectivo")
                electronic_invoice.array_optionals = [wsfe.wsfe.WsfeOptional(2101, self.cbu_transmitter),
                                                      wsfe.wsfe.WsfeOptional(27, self.transfer_option)]

    def _reverse_moves(self, default_values_list=None, cancel=False):
        """ En caso de que esté revirtiendo una factura electrónica y nada más, traigo la original como documento
        asociado. Si quiero revertir más de una FCE, lanzo error.
        """
        values = super(AccountMove, self)._reverse_moves(default_values_list, cancel)
        electronic_invoices_to_reverse = self.filtered(lambda l: l.move_type in ('out_invoice', 'out_refund') \
            and l.voucher_type_id and l.voucher_name and l.document_book_id.book_type_id.is_electronic())
        if electronic_invoices_to_reverse and electronic_invoices_to_reverse == self and len(self) == 1:
            name = self.voucher_name.split('-')
            name = name[1] if len(name) > 1 else name[0]
            values['fce_associated_document_ids'] = [(0, 0, {
                'associated_invoice_id': self.id,
                'point_of_sale': self.journal_id.pos_ar_id.name.lstrip('0'),
                'document_code': self.voucher_type_id.code,
                'document_number': name.lstrip('0'),
                'cuit_transmitter': self.company_id.vat,
                'date': self.invoice_date,
            })]
        elif electronic_invoices_to_reverse:
            raise ValidationError("No se puede realizar la acción de reversión masiva.")
        return values

    def _add_vat_to_electronic_invoice(self, electronic_invoice):
        """ Agrega los impuestos que son iva a informar """
        codes_models_proxy = self.env['codes.models.relation']
        for line in self.line_ids.filtered(lambda x: x.tax_line_id.is_vat and not x.tax_line_id.is_exempt):
            base = sum(
                self.invoice_line_ids.filtered(
                    lambda x: line.tax_line_id in x.tax_ids
                ).mapped('price_subtotal')
            )
            code = int(codes_models_proxy.get_code('account.tax', line.tax_line_id.id, 'Afip'))
            # En casos de multi currency no podemos tomar la base imponible desde la linea
            # que tiene el valor de impuesto, tenemos que buscarla
            # desde la linea de factura
            electronic_invoice.add_iva(documents.tax.Iva(code, abs(line.amount_currency), base))

    def _add_other_tributes_to_electronic_invoice(self, electronic_invoice):
        """ Agrega los impuestos que son percepciones """

        tax_group_internal = self.env['account.tax'].get_internal_tax_group(self.company_id)
        tax_group_perception_iibb = self.env['perception.perception'].get_perception_gross_income_groups(self.company_id)
        tax_group_perception_iva = self.env['perception.perception'].get_perception_vat_groups(self.company_id)

        # Contemplamos 2 casos de tributos que no sean IVA, internos o percepciones.
        for ml in self.line_ids.filtered(lambda t: abs(t.balance) and t.tax_line_id and not t.tax_line_id.is_vat):
            balance = abs(ml.amount_currency if ml.amount_currency else ml.balance)
            base = round(sum(line.price_subtotal for line in self.invoice_line_ids.filtered(
                lambda x: x.product_id and x.product_id.perception_taxable
            )), 2)
            tribute_aliquot = round(balance / base if base else 0, 2)

            if ml.tax_line_id.tax_group_id in (tax_group_perception_iibb | tax_group_perception_iva):
                perception = ml.tax_line_id.perception_id
                if not perception:
                    raise ValidationError("Percepción no encontrada para el impuesto {}".format(ml.tax_line_id.name))
                code = perception.get_afip_code()
                electronic_invoice.add_tribute(documents.tax.Tribute(code, balance, base, tribute_aliquot))

            elif ml.tax_line_id.tax_group_id == tax_group_internal:
                electronic_invoice.add_tribute(documents.tax.Tribute(4, balance, base, tribute_aliquot))
            else:
                raise ValidationError("No se puede informar el impuesto {} a AFIP".format(ml.tax_line_id.name))

    def _get_wsfe(self):
        return self.env['wsaa.configuration'].get_wsfe(self.company_id)

    def _set_empty_invoice_details(self):
        """ Completa los campos de la invoice no establecidos a un default """

        vals = {}

        if not self.afip_concept_id:
            vals['afip_concept_id'] = self._get_afip_concept_based_on_products().id
        if self.env['codes.models.relation'].get_code(
                'afip.concept', self.afip_concept_id.id or vals.get('afip_concept_id'), 'Afip'
        ) in ['2', '3']:
            if not self.date_service_from:
                vals['date_service_from'] = self.invoice_date or fields.Date.context_today(self)
            if not self.date_service_to:
                vals['date_service_to'] = self.invoice_date or fields.Date.context_today(self)

        self.write(vals)

    def _validate_required_electronic_fields(self):
        if not (self.partner_id.vat and self.partner_id.partner_document_type_id):
            raise ValidationError('Por favor, configurar tipo y numero de documento en el cliente')

    def _validate_required_electronic_exportation_fields(self):
        if not self.partner_id.partner_document_type_id:
            raise ValidationError('Por favor, configurar tipo de documento en el cliente')

    def _validate_required_fiscal_electronic_bond_fields(self):
        self._validate_required_electronic_fields()

        denomination_a = self.env.ref('l10n_ar_afip_tables.account_denomination_a')
        cuit = self.env.ref('l10n_ar_afip_tables.partner_document_type_80')
        if self.voucher_type_id.denomination_id == denomination_a and not self.partner_id.partner_document_type_id == cuit:
            raise ValidationError("El tipo de documento del cliente debe ser\
                                  CUIT en comprobantes tipo A.")

        for line in self.invoice_line_ids:
            if any(tax.is_exempt for tax in line.tax_ids) and not self.amount_exempt:
                raise ValidationError("El importe de operaciones exentas debe ser\
                                        mayor a 0 donde exista algun ítem de factura con Iva exento")

    def _get_afip_concept_based_on_products(self):
        """
        Devuelve el concepto de la factura en base a los tipos de productos
        :return: afip.concept, tipo de concepto
        """
        product_types = self.invoice_line_ids.mapped('product_id.type')

        # Estaria bueno pensar una forma para no hardcodearlo, ponerle el concepto en el producto
        # me parecio mucha configuracion a la hora de importar datos o para el cliente, quizas hacer un
        # compute?

        if len(product_types) > 1 and 'service' in product_types:
            # Productos y servicios
            code = '3'
        else:
            if 'service' in product_types:
                # Servicio
                code = '2'
            else:
                # Producto
                code = '1'

        return self.env['codes.models.relation'].get_record_from_code('afip.concept', code, 'Afip')

    # EXPORTACION
    def _get_wsfex(self):
        return self.env['wsaa.configuration'].get_wsfex(self.company_id, self.partner_id)

    @api.returns('self')
    def refund(self, date_invoice=None, date=None, description=None, journal_id=None):
        res = super(AccountMove, self).refund(date_invoice, date, description, journal_id)
        for refund in res:
            refund.date_due = False
        self.env.cr.commit()
        return res

    def action_electronic_exportation(self):
        """
        Realiza el envio a AFIP de la factura de exportacion y escribe en la misma el CAE y su fecha de vencimiento.
        :raises ValidationError: Si el talonario configurado no tiene la misma numeracion que en AFIP.
                                 Si hubo algun error devuelto por afip al momento de enviar los datos.
        """
        self = self.with_context(is_written_from_afip=True)
        electronic_invoices = []
        pos = self.document_book_id.pos_ar_id
        invoices = self.filtered(lambda l: not l.cae and l.amount_total and l.pos_ar_id == pos).sorted(lambda l: l.id)
        sent_invoices = invoices.filtered(lambda x: any(request.result == 'A' for request in x.wsfe_request_detail_ids))
        invoices -= sent_invoices

        # Si hubo un problema despues de escribir una respuesta y no se llegaron a escribir los detalles en las facturas
        for invoice in sent_invoices:
            invoice._write_wsfex_details_on_invoice(
                ast.literal_eval(invoice.wsfe_request_detail_ids[0].request_received)
            )

        if invoices:
            afip_wsfex = self._get_wsfex()
        for invoice in invoices:
            # Validamos los campos
            invoice._validate_required_electronic_exportation_fields()
            # Obtenemos el codigo de comprobante
            document_afip_code = invoice.get_document_afip_code(self.document_book_id)
            # Validamos la numeracion
            self.document_book_id.action_wsfe_number(afip_wsfex, document_afip_code)
            # Armamos la factura
            electronic_invoices.append(invoice._set_electronic_exportation_invoice_details(document_afip_code))

        if electronic_invoices:
            responses = None

            default_cipher = requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS
            requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'AES128-SHA'
            # Chequeamos la conexion y enviamos las facturas a AFIP, guardando el JSON enviado, el response y mostrando
            # los errores (en caso de que los haya)
            try:
                afip_wsfex.check_webservice_status()
                responses, invoice_details = afip_wsfex.get_cae(electronic_invoices, pos.name)
                for r in responses:
                    afip_wsfex.show_error(r)
                if len(responses) != len(invoice_details):
                    raise ValidationError('Las longitudes son distintas')
            except Exception as e:
                raise ValidationError(e.args)
            finally:
                requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = default_cipher
                # Commiteamos para que no haya inconsistencia con la AFIP. Como ya tenemos el CAE escrito en la factura,
                # al validarla nuevamente no se vuelve a enviar y se va a mantener la numeracion correctamente
                if responses:
                    for idx, response in enumerate(responses):
                        if response and response.FEXResultAuth:
                            response_cr = registry(self.env.cr.dbname).cursor()
                            invoices.with_env(self.env(cr=response_cr)).write_wsfex_response(invoice_details[idx], response)
                            response_cr.commit()
                            response_cr.close()

            if responses:
                for idx, response in enumerate(responses):
                    if response and response.FEXResultAuth and response.FEXResultAuth.Resultado != 'R':
                        for invoice in invoices:
                            invoice._update_document_book_and_commit()
                            invoice._write_wsfex_details_on_invoice(zeep.helpers.serialize_object(response))

                    if response and response.FEXResultAuth and response.FEXResultAuth.Resultado == 'R':
                        # Traemos el conjunto de errores
                        errores = '\n'.join(response.FEXResultAuth.Motivos_Obs) \
                            if hasattr(response.FEXResultAuth.Motivos_Obs, 'Observaciones') else ''
                        raise ValidationError('Hubo un error al intentar validar el documento\n{0}'.format(errores))
        self.env.cr.commit()

    def _set_electronic_exportation_invoice_details(self, document_afip_code):
        """ Mapea los valores de ODOO al objeto ExportationElectronicInvoice"""

        self._set_empty_invoice_details()
        codes_models_proxy = self.env['codes.models.relation']

        # Seteamos los campos generales de la factura
        electronic_invoice = wsfex.invoice.ExportationElectronicInvoice(document_afip_code)
        electronic_invoice.document_date = self.invoice_date or fields.Date.context_today(self)
        electronic_invoice.payment_due_date = self.invoice_date_due or fields.Date.context_today(self)
        electronic_invoice.destiny_country = int(codes_models_proxy.get_code(
            'res.country',
            self.partner_id.country_id.id,
            'Afip'
        ))
        electronic_invoice.customer_name = self.partner_id.name
        electronic_invoice.customer_street = self.partner_id.street

        electronic_invoice.destiny_country_cuit = self.partner_id.country_id.vat if \
            self.partner_id.country_id != self.env.ref('base.ar') else self.partner_id.vat
        electronic_invoice.customer_document_type = codes_models_proxy.get_code(
            'partner.document.type',
            self.partner_id.partner_document_type_id.id,
            'Afip'
        )
        electronic_invoice.mon_id = self.env['codes.models.relation'].get_code(
            'res.currency',
            self.currency_id.id,
            'Afip'
        )
        electronic_invoice.mon_cotiz = self.currency_rate or self.current_currency_rate
        electronic_invoice.concept = int(codes_models_proxy.get_code(
            'afip.concept',
            self.afip_concept_id.id,
            'Afip'
        ))
        electronic_invoice.total_amount = self.amount_total
        # 1 = Exportación definitiva de bienes, 2 = Servicios, 4 = Otros
        electronic_invoice.exportation_type = electronic_invoice.concept
        if electronic_invoice.concept == 3:
            electronic_invoice.exportation_type = 4
        # 1: Español, 2: Inglés, 3: Portugués
        electronic_invoice.document_language = 1
        ndc_document_code = int(self.env.ref('l10n_ar_afip_tables.afip_voucher_type_020').code)
        ncc_document_code = int(self.env.ref('l10n_ar_afip_tables.afip_voucher_type_021').code)
        fcc_document_code = int(self.env.ref('l10n_ar_afip_tables.afip_voucher_type_019').code)
        document_codes = [ndc_document_code, ncc_document_code]
        electronic_invoice.existent_permission = '' \
            if (electronic_invoice.exportation_type in [2, 4] and electronic_invoice.document_code == fcc_document_code)\
            or electronic_invoice.document_code in document_codes else 'N'
        electronic_invoice.incoterms = 'CIF'
        # Agregamos items
        electronic_invoice.array_items = self.add_item_exportation()
        self._add_associated_documents_to_electronic_invoice_refund(electronic_invoice)
        return electronic_invoice

    def add_item_exportation(self):
        """ Mapea los valores de ODOO al objeto ExportationElectronicInvoiceItem """
        array_items = []
        for line in self.invoice_line_ids.filtered(lambda l: l.display_type not in ('line_section', 'line_note')):
            item = wsfex.invoice.ExportationElectronicInvoiceItem(line.product_id.name)
            item.quantity = line.quantity
            try:
                item.measurement_unit = self.env['codes.models.relation'].get_code(
                    'product.uom',
                    line.product_uom_id.id,
                    'Afip'
                )
            except:
                item.measurement_unit = 98
            item.unit_price = line.price_unit
            item.bonification = ((line.price_unit * line.quantity) - abs(line.amount_currency)) if line.discount else 0.0
            array_items.append(item)
        return array_items

    def get_document_afip_code(self, document_book):
        """ Busco el codigo del documento de AFIP"""
        return int(document_book.voucher_type_id.code)

    def write_wsfex_response(self, invoice_detail, response):
        """ Escribe el envio y respuesta de un envio a AFIP """

        result = response.FEXResultAuth.Resultado if response.FEXResultAuth else "Error"
        self.env['wsfe.request.detail'].sudo().create({
            'invoice_ids': [(4, invoice.id) for invoice in self],
            'request_sent': invoice_detail,
            'request_received': response,
            'result': result,
            'date': fields.Datetime.now(),
        })

    # BONO FISCAL
    def action_fiscal_electronic_bond(self):
        """
        Realiza el envio a AFIP del bono y escribe en el mismo el CAE y su fecha de vencimiento.
        :raises ValidationError: Si el talonario configurado no tiene la misma numeracion que en AFIP.
                                 Si hubo algun error devuelto por afip al momento de enviar los datos.
        """
        self = self.with_context(is_written_from_afip=True)
        electronic_invoices = []
        pos = self.document_book_id.pos_ar_id
        invoices = self.filtered(lambda l: not l.cae and l.amount_total and l.pos_ar_id == pos).sorted(lambda l: l.id)
        sent_invoices = invoices.filtered(lambda x: any(request.result == 'A' for request in x.wsfe_request_detail_ids))
        invoices -= sent_invoices

        # Si hubo un problema despues de escribir una respuesta y no se llegaron a escribir los detalles en las facturas
        for invoice in sent_invoices:
            invoice._write_wsbfe_details_on_invoice(
                ast.literal_eval(invoice.wsfe_request_detail_ids[0].request_sent),
                ast.literal_eval(invoice.wsfe_request_detail_ids[0].request_received)
            )

        if invoices:
            afip_wsbfe = invoices[0]._get_wsbfe()

        for invoice in invoices:
            # Validamos los campos
            invoice._validate_required_fiscal_electronic_bond_fields()
            # Obtenemos el codigo de comprobante
            document_afip_code = invoice.get_document_afip_code(self.document_book_id)
            # Validamos la numeracion
            self.document_book_id.action_wsfe_number(afip_wsbfe, document_afip_code)
            # Armamos la factura
            electronic_invoices.append(invoice._set_electronic_bond_details(document_afip_code))

        if electronic_invoices:
            responses = None

            default_cipher = requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS
            requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'AES128-SHA'
            # Chequeamos la conexion y enviamos las facturas a AFIP, guardando el JSON enviado, el response y mostrando
            # los errores (en caso de que los haya)
            try:
                afip_wsbfe.check_webservice_status()
                responses, invoice_details = afip_wsbfe.get_cae(electronic_invoices, pos.name)
                for r in responses:
                    afip_wsbfe.show_error(r)
                if len(responses) != len(invoice_details):
                    raise ValidationError('Las longitudes son distintas')
            except Exception as e:
                raise ValidationError(e.args)
            finally:
                requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = default_cipher
                # Commiteamos para que no haya inconsistencia con la AFIP. Como ya tenemos el CAE escrito en el bono,
                # al validarla nuevamente no se vuelve a enviar y se va a mantener la numeracion correctamente
                if responses:
                    for idx, response in enumerate(responses):
                        if response and response.BFEResultAuth:
                            response_cr = registry(self.env.cr.dbname).cursor()
                            invoices.with_env(self.env(cr=response_cr)).write_wsbfe_response(invoice_details[idx], response)
                            response_cr.commit()
                            response_cr.close()
                            # Chequeamos que el resultado no sea rechazado y no haya errores.
                            # Existen casos en que un bono fiscal tiene errores pero no figura como rechazado.
                            # En tales casos no queremos incrementos de numeración ni escritura de detalles como CAE.
                            # Ejemplo: ErrCode: 4881
                            #          ErrMsg: Comprobante asociado PtoVta:X - Tipo:XXX - Nro:XX - OK - en estado autorizado
                            #          y NO RECHAZADO por el Comprador. Para autorizar un comprobante de anulacion como el
                            #          que intenta autorizar, el comprobante asociado debe estar rechazado por el comprador.
                            if response.BFEResultAuth.Resultado != 'R' and not response.BFEErr.ErrMsg != 'OK':
                                for invoice in invoices:
                                    invoice._update_document_book_and_commit()
                                    invoice._write_wsbfe_details_on_invoice(
                                        zeep.helpers.serialize_object(invoice_details[idx]),
                                        zeep.helpers.serialize_object(response),
                                    )
                            elif response.BFEResultAuth.Resultado == 'R':
                                # Traemos el conjunto de observaciones
                                errores = '\n'.join(response.BFEResultAuth.Obs) \
                                    if hasattr(response.BFEResultAuth.Obs, 'Observaciones') else ''
                                raise ValidationError('Hubo un error al intentar validar el documento\n{0}'.format(errores))
        self.env.cr.commit()

    def _set_electronic_bond_details(self, document_afip_code):
        """ Mapea los valores de ODOO al objeto FiscalElectronicBond"""

        denomination_c = self.env.ref('l10n_ar_afip_tables.account_denomination_c')
        codes_models_proxy = self.env['codes.models.relation']

        # Seteamos los campos generales del bono
        electronic_bond = wsbfe.invoice.FiscalElectronicBond(document_afip_code)
        electronic_bond.taxed_amount = self.amount_to_tax
        electronic_bond.untaxed_amount = self.amount_not_taxable if self.voucher_type_id.denomination_id != denomination_c else 0
        electronic_bond.exempt_amount = self.amount_exempt if self.voucher_type_id.denomination_id != denomination_c else 0
        electronic_bond.document_date = self.invoice_date or fields.Date.context_today(self)
        electronic_bond.payment_due_date = self.invoice_date_due or fields.Date.context_today(self)
        electronic_bond.customer_document_number = self.partner_id.vat
        electronic_bond.customer_document_type = codes_models_proxy.get_code(
            'partner.document.type',
            self.partner_id.partner_document_type_id.id,
            'Afip'
        )
        electronic_bond.mon_id = self.env['codes.models.relation'].get_code(
            'res.currency',
            self.currency_id.id,
            'Afip'
        )
        electronic_bond.mon_cotiz = self.currency_rate or self.current_currency_rate
        electronic_bond.zone_id = 0 #Por el momento se utiliza 0

        # Agrego items
        electronic_bond.array_items = self.add_item_bond()
        # Agregamos impuestos y percepciones
        electronic_bond.total_amount = self.amount_total
        perceptions_amount = self.get_perceptions_amount()
        electronic_bond.reception_amount = perceptions_amount['total']
        electronic_bond.municipal_reception_amount = perceptions_amount['mun']
        electronic_bond.iibb_amount = perceptions_amount['gross_income']
        pay_off_tax_amount = 0.00
        for line in self.line_ids.filtered(lambda x: x.tax_line_id.is_vat and not x.tax_line_id.is_exempt):
            pay_off_tax_amount += line.price_subtotal
        electronic_bond.pay_off_tax_amount = pay_off_tax_amount
        electronic_bond.rni_pay_off_tax_amount = 0.00
        electronic_bond.internal_tax_amount = 0.00
        # Agregamos los documentos asociados para Notas de débito o crédito
        self._add_associated_documents_to_electronic_invoice_refund(electronic_bond)
        # Agregamos lo exclusivo de facturas de crédito
        self._add_optionals_to_credit_invoice(electronic_bond)

        return electronic_bond

    def add_item_bond(self):
        """ Mapea los valores de ODOO al objeto FiscalElectronicBondItem """
        array_items = []
        for line in self.invoice_line_ids.filtered(lambda l: l.display_type not in ('line_section', 'line_note')):

            try:
                measurement_unit = self.env['codes.models.relation'].get_code(
                    'product.uom',
                    line.uom_id.id,
                    'Afip'
                )
            except:
                measurement_unit = 98
            unit_price = line.price_unit
            bonification = ((line.price_unit * line.quantity) - line.price_subtotal) if line.discount else 0.0
            iva_id = self.env['codes.models.relation'].get_code('account.tax', line.tax_ids[0].id, 'Afip') if line.tax_ids else 0
            product_ncm_code = self.check_product(line)
            ncm_code = product_ncm_code
            item = wsbfe.invoice.FiscalElectronicBondItem(ncm_code, line.product_id.name, line.quantity, measurement_unit, unit_price, bonification, iva_id)
            array_items.append(item)

        return array_items

    def check_product(self, invoice_line):
        """ Chequeo que tenga producto y este nomenclado"""
        if not invoice_line.product_id:
            raise ValidationError('Las lineas deben contener productos.')
        if not invoice_line.product_id.ncm_id:
            raise ValidationError('Es necesario que el producto {} este nomenclado.'.format(invoice_line.product_id.name))
        return invoice_line.product_id.ncm_id.code

    def _get_wsbfe(self):
        return self.env['wsaa.configuration'].get_wsbfe(self.company_id)

    def get_perceptions_amount(self):
        total_amount = 0
        mun_perceptions_amount = 0
        gross_income_amount = 0
        for perception in self.perception_ids:
            total_amount += perception.amount
            if perception.perception_id.jurisdiction == 'municipal':
                mun_perceptions_amount += perception.amount
            if perception.perception_id.type == 'gross_income':
                gross_income_amount += perception.amount

        perceptions_amount = {'total': total_amount,
                              'mun': mun_perceptions_amount,
                              'gross_income': gross_income_amount}
        return perceptions_amount

    def write_wsbfe_response(self, invoice_detail, response):
        """ Escribe el envio y respuesta de un envio a AFIP """
        if response.BFEResultAuth:
            # Nos traemos el offset de la zona horaria para dejar en la base en UTC como corresponde
            offset = datetime.now(pytz.timezone('America/Argentina/Buenos_Aires')).utcoffset().total_seconds() / 3600
            fch_proceso = datetime.now() - relativedelta(hours=offset)
            result = response.BFEResultAuth.Resultado
            date = fch_proceso
        else:
            result = "Error"
            date = fields.Datetime.now()

        self.env['wsfe.request.detail'].sudo().create({
            'invoice_ids': [(4, id) for id in self.ids],
            'request_sent': invoice_detail,
            'request_received': response,
            'result': result,
            'date': date
        })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
