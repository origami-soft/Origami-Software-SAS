#!/usr/bin/env python
# coding: utf-8

from odoo import api, SUPERUSER_ID

def parse_code(code):
        currency_start = code.find("env.ref('") + len("env.ref('")
        currency_end = code.find("')", currency_start)
        company_start = code.find("env['res.company'].browse(") + len("env['res.company'].browse(")
        company_end = code.find(")", company_start)

        if currency_start != -1 and currency_end != -1:
            currency_ref = code[currency_start:currency_end]
            if company_start != -1 and company_end != -1:
                company_str = code[company_start:company_end]
                if company_str.isdigit():
                    company_id = int(company_str)
                else:
                    company_id = None
            else:
                company_id = None
            return currency_ref, company_id
        else:
            return None, None

def migrate(cr, installed_version):  
    env = api.Environment(cr, SUPERUSER_ID, {})
    afip_cron_jobs = env['ir.cron'].search([('code', 'ilike', 'set_cotization_from_afip')])

    # Crear una lista vacía para almacenar las tuplas (currency_ref, company_id)
    data_to_insert = []

    for job in afip_cron_jobs:
        currency_ref, company_id = parse_code(job.code)
        currency_id = env.ref(currency_ref).id
        if not company_id:
            company_id = job.user_id.company_id.id
        if currency_id:
            data_to_insert.append((currency_id, company_id))

    # Crear la tabla currency_company_info e insertar los datos
    if data_to_insert:
        afip_cron_jobs.unlink()
        cr.execute("""
            SELECT * INTO currency_company_info 
            FROM (VALUES %s) AS t (currency_id, company_id)
        """ % ','.join(['(%s, %s)' for _ in data_to_insert]),
        tuple(item for sublist in data_to_insert for item in sublist))