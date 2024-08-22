#!/usr/bin/env python
# coding: utf-8

from odoo import api, SUPERUSER_ID


def migrate(cr, installed_version):
    # env = api.Environment(cr, SUPERUSER_ID, {})
    env = api.Environment(cr, SUPERUSER_ID, {})
    cr.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'currency_company_info'
        )
    """)

    if cr.fetchone()[0]:
        # Obtener los datos de la tabla currency_company_info
        cr.execute("""
            SELECT company_id, currency_id
            FROM currency_company_info;
        """)

        # Crear un diccionario para almacenar las monedas por compañía
        company_currencies = {}
        
        for row in cr.fetchall():
            company_id, currency_id = row
            
            # Agregar la moneda a la lista correspondiente a la compañía
            if company_id not in company_currencies:
                company_currencies[company_id] = []
            company_currencies[company_id].append(currency_id)

        # Crear registros para cada compañía y sus monedas
        for company_id, currency_ids in company_currencies.items():
            vals = {
                'service': 'AFIP',
                'company_id': company_id,
                'currency_ids': [(6, 0, currency_ids)]
            }
            
            env['res.currency.rate.provider'].create(vals)

        cr.execute("""
            DROP TABLE currency_company_info;
        """)