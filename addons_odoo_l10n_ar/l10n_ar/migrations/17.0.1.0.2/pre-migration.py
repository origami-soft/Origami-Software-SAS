from odoo import api, SUPERUSER_ID
import logging
from odoo.upgrade import util

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    # env = api.Environment(cr, SUPERUSER_ID, {})
    #
    # cr.execute("""
    #     DELETE FROM res_country WHERE code IS NULL OR code = 'f' OR code = '';
    # """)
    #
    # cr.commit()

    env = util.env(cr)

    countrys = env["res.country"].sudo().search([('code', '=', False)])
    for country in countrys:
        country.unlink()

    _logger.info("YUYU Updated %s countrys", len(countrys))
