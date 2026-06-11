#!/usr/bin/env python
# coding: utf-8

import logging

_logger = logging.getLogger(__name__)

try:
    # Available only during a real upgrade run (upgrade-util on the path).
    from odoo.upgrade import util
except ImportError:
    util = None

# (old_name -> new_name) pairs to promote the official l10n_ar modules to the
# Blueorange-branded names so the BO modules load on top of existing data.
RENAMES = [
    ('l10n_ar', 'l10n_ar_bo'),
    ('l10n_ar_stock', 'l10n_ar_stock_bo'),
    ('l10n_ar_website_sale', 'l10n_ar_website_sale_price'),
    ('l10n_ar_pos_invoicing', 'l10n_ar_afip_pos_invoicing'),
]


def _module_state(cr, name):
    cr.execute("SELECT id, state FROM ir_module_module WHERE name = %s", (name,))
    return cr.fetchone()


def _remove_stub(cr, name):
    """Remove an uninstalled module record (a stub created by the addons scan).

    Refuses to touch a module that holds live data (any installed-ish state),
    so a re-run can never wipe an already-migrated module.
    """
    row = _module_state(cr, name)
    if not row:
        return
    mod_id, state = row
    if state not in ('uninstalled', 'uninstallable', 'to install'):
        _logger.warning(
            "base_vat_ar migration: refuse to remove module %r in state %r",
            name, state)
        return
    # Data owned BY the stub module (none if never installed) ...
    cr.execute("DELETE FROM ir_model_data WHERE module = %s", (name,))
    # ... and the module's own identity xmlid owned by `base`, otherwise the
    # later rename of the old module's xmlid collides with this dangling row.
    cr.execute(
        "DELETE FROM ir_model_data WHERE module = 'base' AND name = %s",
        ('module_%s' % name,))
    cr.execute("DELETE FROM ir_module_module_dependency WHERE module_id = %s", (mod_id,))
    cr.execute("DELETE FROM ir_module_module WHERE id = %s", (mod_id,))


def _rename_module_sql(cr, old, new):
    cr.execute("UPDATE ir_module_module SET name = %s WHERE name = %s", (new, old))
    cr.execute("UPDATE ir_module_module_dependency SET name = %s WHERE name = %s", (new, old))
    cr.execute("UPDATE ir_model_data SET module = %s WHERE module = %s", (new, old))
    cr.execute(
        "UPDATE ir_model_data SET name = %s WHERE module = 'base' AND name = %s",
        ('module_%s' % new, 'module_%s' % old))


def migrate(cr, installed_version):
    for old, new in RENAMES:
        # Idempotency guard: act only while the OLD module still exists.
        # If old is gone, this pair was already migrated -> never touch `new`.
        if not _module_state(cr, old):
            _logger.info("base_vat_ar migration: %r already migrated, skipping", old)
            continue

        if util is not None:
            util.remove_module(cr, new)
            util.rename_module(cr, old, new)
        else:
            _remove_stub(cr, new)
            _rename_module_sql(cr, old, new)
        _logger.info("base_vat_ar migration: renamed %r -> %r", old, new)
