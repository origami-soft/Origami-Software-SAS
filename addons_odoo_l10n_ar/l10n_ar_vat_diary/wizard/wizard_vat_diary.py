from odoo import models, fields, http, api


class WizardVatDiary(models.TransientModel):
    _name = 'wizard.vat.diary'
    _description = 'Wizard de libro de IVA'

