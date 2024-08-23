# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID, api


def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.ref('l10n_ar_bank_reconcile.account_bank_reconcile_multi').domain_force = "['|',('company_id','=',False),('company_id', 'in', company_ids)]"
    env.ref('l10n_ar_bank_reconcile.account_bank_reconcile_line_multi').domain_force = "['|',('company_id','=',False),('company_id', 'in', company_ids)]"
    env.ref('l10n_ar_bank_reconcile.account_reconcile_move_line_multi').domain_force = "['|',('company_id','=',False),('company_id', 'in', company_ids)]"