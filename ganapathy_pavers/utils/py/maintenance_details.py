from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
def batch_customization():
    batch_custom_fields()
def batch_custom_fields():
    custom_fields = {
        "Maintenance Details": [
            dict(
                fieldname="reference_no",
                fieldtype="Data",
                label="Reference No",
                insert_after="maintenance"
            )
            ]
    }
    create_custom_fields(custom_fields)
    