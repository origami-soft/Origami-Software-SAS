# -*- encoding: utf-8 -*-

from odoo import models

class PosAr(models.Model):
    _inherit = 'pos.ar'

    def get_available_documents(self, params):
        """Heredo método para tener en cuenta que si en params
        llega que se busquen notas de débito debo devolver los
        talonarios cuyo tipo de comprobante es nota de débito.
        """        
        dbooks = super().get_available_documents(params)
        return dbooks.filtered(
            lambda db:
            (db.voucher_type_id.is_debit_note if 'debit_note' in params else True)
        )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
