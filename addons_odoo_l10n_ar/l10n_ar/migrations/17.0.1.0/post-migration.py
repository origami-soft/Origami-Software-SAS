from odoo import api, SUPERUSER_ID

def migrate(cr, version):


    cr.execute("""
            DELETE FROM ir_model_data
            WHERE model = 'retention.retention.template';
        """)

    # Eliminar campos de selección relacionados en ir_model_fields
    cr.execute("""
            DELETE FROM ir_model_fields
            WHERE model = 'retention.retention.template';
        """)

    # Eliminar cualquier campo dependiente en otras tablas
    cr.execute("""
            DELETE FROM ir_model_fields_selection
            WHERE field_id IN (
                SELECT id FROM ir_model_fields 
                WHERE model = 'retention.retention.template'
            );
        """)

    cr.execute("""
            DELETE FROM ir_model_data
            WHERE model = 'perception.perception.template';
        """)

    # Eliminar campos de selección relacionados en ir_model_fields
    cr.execute("""
            DELETE FROM ir_model_fields
            WHERE model = 'perception.perception.template';
        """)

    # Eliminar cualquier campo dependiente en otras tablas
    cr.execute("""
            DELETE FROM ir_model_fields_selection
            WHERE field_id IN (
                SELECT id FROM ir_model_fields 
                WHERE model = 'perception.perception.template'
            );
        """)

    cr.execute("""
            DELETE FROM ir_model_data
            WHERE model = 'account.tax.ar.template';
        """)

    # Eliminar campos de selección relacionados en ir_model_fields
    cr.execute("""
            DELETE FROM ir_model_fields
            WHERE model = 'account.tax.ar.template';
        """)

    # Eliminar cualquier campo dependiente en otras tablas
    cr.execute("""
            DELETE FROM ir_model_fields_selection
            WHERE field_id IN (
                SELECT id FROM ir_model_fields 
                WHERE model = 'account.tax.ar.template'
            );
        """)

    cr.execute("""
            DELETE FROM ir_model_data
            WHERE model = 'account.tax.template';
        """)

    # Eliminar campos de selección relacionados en ir_model_fields
    cr.execute("""
            DELETE FROM ir_model_fields
            WHERE model = 'account.tax.template';
        """)

    # Eliminar cualquier campo dependiente en otras tablas
    cr.execute("""
            DELETE FROM ir_model_fields_selection
            WHERE field_id IN (
                SELECT id FROM ir_model_fields 
                WHERE model = 'account.tax.template'
            );
        """)
