import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
def gl_entry_customization():
    custom_fields={
    "GL Entry": [
            dict(
            fieldname='type',
            label='Type',
            fieldtype='Data',
            insert_after='project'
            ),
            
    ]
    }
    create_custom_fields(custom_fields)