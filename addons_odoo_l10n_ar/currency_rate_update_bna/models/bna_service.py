# -*- coding: utf-8 -*-

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