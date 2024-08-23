# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID, api


def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.cr.execute("select id from retention_activity where code = 965")
    act_965 = env.cr.fetchone()
    if act_965:
        act_965 = act_965[0]
        act_965_ext_id = env['ir.model.data'].search([('model', '=', 'retention.activity'), ('res_id', '=', act_965)])
        if not act_965_ext_id:
            env['ir.model.data'].create({
                'module': 'l10n_ar_retentions',
                'name': 'ret_act_965',
                'model': 'retention.activity',
                'res_id': act_965,
            })
