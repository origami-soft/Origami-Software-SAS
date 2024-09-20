from odoo import api, SUPERUSER_ID

def migrate(cr, version):
    """
    Eliminar referencias al modelo retention.retention.template
    """
    if not version:
        return

    # Eliminar referencias huérfanas en ir_model_fields
    cr.execute("""
        DELETE FROM ir_model_fields
        WHERE model = 'retention.retention.template';
    """)

    # Eliminar datos de selección huérfanos en ir_model_data
    cr.execute("""
        DELETE FROM ir_model_data
        WHERE name LIKE 'l10n_ar.selection__retention_retention_template__%';
    """)

    # Eliminar posibles referencias en cualquier otra tabla relevante
    cr.execute("""
        DELETE FROM ir_model_fields_selection
        WHERE field_id IN (
            SELECT id FROM ir_model_fields WHERE model = 'retention.retention.template'
        );
    """)
