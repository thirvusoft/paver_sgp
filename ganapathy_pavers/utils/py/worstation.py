import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
def item_customization():
        custom_fields={
        "workstation":[
            dict(
            fieldname='assets_table_worksation',
            label='Assets',
            fieldtype='Table',
            options="Asset_table",
            insert_after='ts_labor'
            ),
        ]
        }

        create_custom_fields(custom_fields)
