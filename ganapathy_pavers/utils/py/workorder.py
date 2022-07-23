from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
def workorder_customization():
        workorder_custom_fields={
        "Work Order":[
            dict(
            fieldname='mould_name',
            label='Mould Name',
            fieldtype='Link',
            options="Asset",
            insert_after='bom_no'
            ),
 
        ]
        }

        create_custom_fields(workorder_custom_fields)
