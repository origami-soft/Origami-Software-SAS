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

import requests
from odoo.exceptions import ValidationError
API_URL = 'https://funny-ant-20.deno.dev/api/bna'

class BNAService:
    def __init__(self, moneda):
        self._moneda = moneda

    @property
    def moneda(self):
        return self._moneda

    def get_cotization_from_bna(self, service):
        data = {"name": self.moneda, "service": "BILL"}
        if service == 'BNA-DIV':
            data = {"name": self.moneda, "service": "DIV"}
        headers = {'Content-type': 'application/json'}
        response = requests.post(API_URL, json=data, headers=headers)
        if response.ok:
            # Procesa la respuesta exitosa
            return response.json()
        else:
            raise ValidationError(response.text)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: