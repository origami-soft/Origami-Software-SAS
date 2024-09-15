# -*- coding: utf-8 -*-

import base64

from odoo import http
from odoo.addons.web.controllers.main import content_disposition
import json, logging
_logger = logging.getLogger(__name__)
from werkzeug.exceptions import InternalServerError



class WizardGeneralLedgerExcelRoute(http.Controller):
    @http.route('/web/binary/download_general_ledger', type='http', auth="public")
    def download_general_ledger(self, debug=1, wizard_id=0, filename=''):  # pragma: no cover
        """ Descarga un documento cuando se accede a la url especificada en http route.
        :param debug: Si esta o no en modo debug.
        :param int wizard_id: Id del modelo que contiene el documento.
        :param filename: Nombre del archivo.
        :returns: :class:`werkzeug.wrappers.Response`, descarga del archivo excel.
        """
        try:
            file = base64.b64decode(http.request.env['wizard.general.ledger.excel'].browse(int(wizard_id)).ledger or '')
            return http.request.make_response(file, [('Content-Type', 'application/excel'), ('Content-Disposition', content_disposition(filename))])
        except Exception as exc:
            _logger.exception("Excepción durante el manejo de solicitudes")
            payload = json.dumps({
                'code': 200,
                'message': "Odoo Server Error",
                'data': http.serialize_exception(exc)
            })
            raise InternalServerError(payload) from exc

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
