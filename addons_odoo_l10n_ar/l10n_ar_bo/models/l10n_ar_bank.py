# - coding: utf-8 -*-

from odoo import models, api
from odoo.exceptions import ValidationError
from l10n_ar_api.padron import banks


class Bank(models.Model):
    _inherit = 'res.bank'

    @api.model
    def update_module(self):
        try:
            self.update_banks()
        except:
            pass

    def update_banks(self):
        """ Actualiza o crea los bancos de argentina segun los registros de AFIP """
        banks_class = banks.Banks
        try:
            data_get = banks_class.get_values(banks_class.get_banks_list())
        except:
            raise ValidationError(
                "Se ha producido un error al intentar descargar los bancos desde AFIP. Inténtelo más tarde"
            )

        afip_banks = {element.get('code'): element.get('name') for element in data_get}

        # Traigo los bancos de Argentina de la base
        ar_country = self.env.ref('base.ar')
        bank_proxy = self.env['res.bank']
        base_banks = bank_proxy.search([('country', '=', ar_country.id)])

        # Recorro el diccionario de bancos. Si encuentro el codigo en los que existen en el
        # sistema, sobreescribo el nombre, sino lo creo.
        for key, value in afip_banks.items():
            bank_to_update = base_banks.filtered(lambda r: r.bic == key)
            if bank_to_update:
                bank_to_update.write({'name': value})
            else:
                bank_proxy.create({'name': value, 'bic': key, 'country': ar_country.id})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
